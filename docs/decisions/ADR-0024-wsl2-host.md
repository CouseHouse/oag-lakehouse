# ADR-0024: whole local stack in WSL2 on the workstation

Status: accepted 2026-09-26. SPEC.md D24.

## Context

The original prompt placed the Docker Compose data plane on a Proxmox VM and vLLM on the
workstation. Every service is a container either way; the VM only chose which kernel hosts
the Docker daemon. The workstation was measured at an i9-14900K, 64 GB DDR5, RTX 5090 32 GB,
a 1 TB WSL2 virtual disk with about 740 GB free on the host NVMe, Docker Desktop installed.

## Decision

Run the data plane, vLLM, and the agent in WSL2 on the workstation through Docker Desktop.
Raise the WSL2 memory limit to 24 GB for Phases 1 to 3 and 48 GB from Phase 4, leaving
16 GB for Windows.

## Consequences

One host, no LAN networking, no mirrored-mode port forwarding. vLLM runs as a Compose service
on the shared network, so `model.base_url` is `http://vllm:8000/v1` inside containers. Every
endpoint is config, so moving the data plane out later is a `config/local.yaml` change.
Rejected: Proxmox VM (second kernel's RAM, cross-host networking for no design benefit),
Docker in a Proxmox LXC (unsupported, fragile bind mounts), Docker on the Proxmox host
(conflicts with Proxmox networking).
