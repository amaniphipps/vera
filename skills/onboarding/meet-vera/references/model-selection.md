# Model selection — RevenueBench + OpenRouter evidence workflow

Vera is model-agnostic and multimodal by configuration. Use current public
evidence, never a hardcoded leaderboard.

## Sources (see decisions/benchmark-sources.yaml)

- RevenueBench results: RevOps task scores, latency, coverage, modality metadata.
  Compare only full-coverage rows; label partials partial. Record Last refreshed.
- OpenRouter catalog: current IDs, availability, pricing, context, input/output
  modalities. Record fetch timestamp.

## Procedure

1. Ask deployment preference: hosted frontier | hosted open-weight |
   local open-weight | no preference/mixed.
2. Ask priority (cost|quality|speed), budget hint, required modalities, and
   local hardware constraints when local is requested.
3. Refresh both sources; retain URLs, timestamps, errors. Public reads only.
4. Filter by actual account/provider access, runtime support, required
   modalities, context, local feasibility.
5. Score by decisions/interface.yaml. RevenueBench → domain quality;
   OpenRouter → availability/pricing/context/modalities. Frontier docs may
   supplement frontier-specific capabilities.
6. Return 1 recommendation + 2 alternatives, each with model, deployment,
   one-line rationale, benchmark evidence/date, price/context/modalities,
   limitations.
7. Record choice + evidence pointer in working profile. Rankings are cached
   public data, not durable personal memory.

## Failure modes

Source unavailable → name which source failed, give cached timestamp if any,
keep working model, never invent a ranking. Local models need hardware/install
disclosure; never claim bundled credits or free trial. Same procedure on
Hermes and OpenCode.
