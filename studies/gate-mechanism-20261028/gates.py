"""Bounded coefficient residual gate for the 2026-10-28 matched mechanism study.

Both arms execute the same pooling/projection/MLP operations and have 29,380
parameters.  The constant arm removes current-frame descriptor information only
after pooling.  No annotations, tokens, split identifiers or predictions enter
this module.
"""
import torch
from torch import nn


class BoundedResidualGate(nn.Module):
    def __init__(self, baseline_logits, constant_descriptor=False):
        super().__init__()
        alpha = torch.as_tensor(baseline_logits, dtype=torch.float32).detach().clone()
        if alpha.shape != (4,) or not torch.isfinite(alpha).all():
            raise ValueError("Four finite legacy encoder logits are required")
        self.camera_channels = 256
        self.lidar_channels = 64
        self.detach_features = True
        self.camera_projection = nn.Linear(256, 64)
        self.lidar_projection = nn.Linear(64, 64)
        self.norm = nn.LayerNorm(128)
        self.hidden = nn.Linear(128, 64)
        self.activation = nn.GELU()
        self.output = nn.Linear(64, 4)
        self.register_buffer("baseline_logits", alpha)
        w0 = alpha.sigmoid()
        self.register_buffer("baseline_weights", w0)
        self.register_buffer("amplitude", torch.minimum(
            torch.full_like(w0, 0.1), torch.minimum(w0, 1.0 - w0)))
        self.register_buffer("constant_descriptor", torch.tensor(
            bool(constant_descriptor), dtype=torch.bool))
        nn.init.zeros_(self.output.weight)
        nn.init.zeros_(self.output.bias)
        self.last_raw_output = None

    def descriptor_hidden(self, camera, lidar):
        levels = [camera] if isinstance(camera, torch.Tensor) else list(camera)
        if not levels or lidar.ndim != 4 or lidar.shape[1] != 64 or min(lidar.shape) == 0:
            raise ValueError("Expected FPN levels and nonempty LiDAR [B,64,H,W]")
        pooled = []
        for x in levels:
            if x.ndim != 5 or x.shape[0] != lidar.shape[0] or x.shape[2] != 256 or min(x.shape) == 0:
                raise ValueError("Each camera level must be nonempty [B,V,256,H,W]")
            if x.device != lidar.device:
                raise ValueError("Sensor feature devices differ")
            pooled.append(x.detach().float().mean(dim=(1, 3, 4)))
        cam = torch.stack(pooled).mean(dim=0).to(self.camera_projection.weight.dtype)
        lid = lidar.detach().float().mean(dim=(2, 3)).to(self.lidar_projection.weight.dtype)
        # Both modes run the identical operation graph; only this scalar selects
        # whether pooled sensor values or fixed nonzero descriptors are retained.
        cam = torch.where(self.constant_descriptor, torch.ones_like(cam), cam)
        lid = torch.where(self.constant_descriptor, torch.ones_like(lid), lid)
        descriptor = torch.cat((self.camera_projection(cam), self.lidar_projection(lid)), dim=-1)
        return self.activation(self.hidden(self.norm(descriptor)))

    def forward(self, camera, lidar):
        raw = self.output(self.descriptor_hidden(camera, lidar))
        self.last_raw_output = raw.detach()
        return self.baseline_weights[None, :] + self.amplitude[None, :] * torch.tanh(raw)


def mask_decoder_lidar_input(module, args):
    """Pre-hook diagnostic: zero only LiDAR half of decoder concat features.

    The complete LiDAR interpolation/projection/normalization branch has already
    executed.  This is an inference-only intervention, not a trained comparison.
    """
    if len(args) != 1 or args[0].shape[-1] != 512:
        raise ValueError("Expected one decoder fusion tensor with 512 channels")
    x = args[0]
    return (torch.cat((x[..., :256], x[..., 256:] * 0.0), dim=-1),)


def verify_contract():
    """CPU-only synthetic implementation checks; no detection evidence or GPU.

    This also checks the expected zero-head first-gradient bottleneck: output
    parameters learn on the first step; earlier descriptor parameters acquire a
    gradient only after the output weight has moved away from zero.
    """
    import copy
    torch.manual_seed(528)
    alpha = torch.tensor([-1.0, -0.1, 0.4, 1.5])
    dynamic = BoundedResidualGate(alpha)
    constant = copy.deepcopy(dynamic)
    constant.constant_descriptor.fill_(True)
    n1 = sum(p.numel() for p in dynamic.parameters())
    n2 = sum(p.numel() for p in constant.parameters())
    assert n1 == n2 == 29380
    assert all(torch.equal(p1, p2) for p1, p2 in zip(dynamic.parameters(), constant.parameters()))
    camera = [torch.randn(2, 3, 256, 4, 3, requires_grad=True),
              torch.randn(2, 3, 256, 2, 2, requires_grad=True)]
    lidar = torch.randn(2, 64, 5, 4, requires_grad=True)
    expected = alpha.sigmoid()[None, :].expand(2, -1)
    assert torch.equal(dynamic(camera, lidar), expected)
    assert torch.equal(constant(camera, lidar), expected)
    loss = (dynamic(camera, lidar) * torch.tensor([1.0, 2.0, 3.0, 4.0])).sum()
    loss.backward()
    assert all(x.grad is None for x in camera) and lidar.grad is None
    assert dynamic.output.weight.grad.abs().sum().item() > 0
    assert dynamic.output.bias.grad.abs().sum().item() > 0
    assert dynamic.hidden.weight.grad is not None and dynamic.hidden.weight.grad.abs().sum().item() == 0
    assert dynamic.camera_projection.weight.grad is not None and dynamic.camera_projection.weight.grad.abs().sum().item() == 0
    assert dynamic.lidar_projection.weight.grad is not None and dynamic.lidar_projection.weight.grad.abs().sum().item() == 0
    with torch.no_grad():
        dynamic.output.weight.add_(dynamic.output.weight.grad, alpha=-0.1)
        dynamic.output.bias.add_(dynamic.output.bias.grad, alpha=-0.1)
    dynamic.zero_grad(set_to_none=True)
    (dynamic(camera, lidar) * torch.tensor([1.0, 2.0, 3.0, 4.0])).sum().backward()
    assert dynamic.hidden.weight.grad.abs().sum().item() > 0
    assert dynamic.camera_projection.weight.grad.abs().sum().item() > 0
    assert dynamic.lidar_projection.weight.grad.abs().sum().item() > 0
    assert all(x.grad is None for x in camera) and lidar.grad is None
    # After a head change the constant arm remains identical for distinct frames.
    with torch.no_grad():
        constant.output.weight.fill_(0.03)
        const1 = constant(camera, lidar)
        const2 = constant([x * 17 + 2 for x in camera], lidar * -5)
    assert torch.equal(const1, const2)
    extreme = BoundedResidualGate(torch.tensor([-100.0, -0.2, 0.6, 100.0]))
    with torch.no_grad():
        extreme.output.weight.zero_()
        extreme.output.bias.copy_(torch.tensor([-1e6, 1e6, -1e6, 1e6]))
        weights = extreme(camera, lidar)
        assert torch.isfinite(weights).all()
        assert ((weights >= 0) & (weights <= 1)).all()
        assert (torch.abs(weights - extreme.baseline_weights) <= extreme.amplitude + 1e-7).all()
    # The diagnostic preserves encoder half and zeros exactly the decoder half.
    x = torch.arange(1024, dtype=torch.float32).reshape(1, 2, 512)
    masked = mask_decoder_lidar_input(None, (x,))[0]
    assert torch.equal(masked[..., :256], x[..., :256])
    assert torch.count_nonzero(masked[..., 256:]).item() == 0
    return {"status": "PASS", "device": "cpu", "same_arm_parameters": n1,
            "neutral_equality": True, "coefficient_bounds": True,
            "input_descriptors_detached": True, "constant_descriptor_invariance": True,
            "first_step_output_gradient_only": True, "second_step_projection_hidden_gradients": True,
            "decoder_input_half_mask": True,
            "scope": "synthetic implementation contract only; no real detection benefit"}
