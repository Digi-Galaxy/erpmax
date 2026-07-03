# VPS Access

## Host
- Alias: `ukvps`
- Public IP: `168.231.78.48`
- Tailscale IP: `100.75.116.86`
- User: `dg`

## SSH Key
- Local key: `~/.ssh/galaxylab_vps_ed25519`
- Public key: `~/.ssh/galaxylab_vps_ed25519.pub`

## Suggested SSH Config
```sshconfig
Host ukvps
    HostName 100.75.116.86
    User dg
    IdentityFile ~/.ssh/galaxylab_vps_ed25519
```

## Direct Connect
```bash
ssh -F /dev/null -i ~/.ssh/galaxylab_vps_ed25519 dg@100.75.116.86
```

## Notes
- Use Tailscale first when public SSH is blocked.
- Use `sudo -S` with the `dg` password for privileged commands.
- If SSH config breaks, bypass it with `-F /dev/null`.
