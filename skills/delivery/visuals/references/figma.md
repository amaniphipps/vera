# Reading Figma files

Read-only guidance for pulling design structure and tokens from a Figma file when the user connects one.

## What to read

- Frames, components, and their structure, to reconstruct a screen.
- Design tokens: colors, type scale, spacing, radii. Map these to brand tokens.
- Component variants and properties, to pick the right states.

## Procedure

- Resolve the file or team from the slots in org.example.yaml. If the user gave a specific file link, use that.
- List top-level frames first to orient, then drill into the frame you need.
- Pull tokens from the design system file, not from a single screen.

## Token mapping

Map design tokens to brand tokens when your toolchain needs named tokens rather than raw values. Write the mapping down before using it so later drift is visible:

```
design.color.primary -> brand.color.primary
design.color.ink     -> brand.color.text
design.type.body     -> brand.font.body
```

Do not hardcode raw hex values into deliverables. Reference the token name so a palette change flows through.

## Pitfalls

- Rate limits. Space paged calls, honor Retry-After, avoid parallel scans.
- Some token or folder endpoints need extra scopes. If a call 403s, note the missing scope and work around via other read endpoints.
- Node ids: URLs and APIs can use different id formats. Confirm which is which.