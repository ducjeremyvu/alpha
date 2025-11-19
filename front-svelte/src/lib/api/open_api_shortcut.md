# API - Frontend Interface 

Yeah… that’s the tax you pay for being both backend-engineer and frontend-engineer of your own little trading empire.

When your FastAPI endpoint changes shape, TypeScript isn’t magic — it only knows what **you** tell it.
If the backend suddenly returns:

```json
{
  data: { all: {...}, foo: 123 },
  metrics: { prev_day: {...}, extra: true }
}
```

…but your Svelte types don’t match?
TS will bark, the UI might break, and you’ll wonder why decimals suddenly became undefined.

Here’s the good news: **you don’t need to manually chase every small change** if you adopt one simple practice.

### The sane workflow when you iterate fast

You’re moving fast, experimenting, adding new metrics daily.
So treat your TS types as:

• strict where it matters
• loose where you’re still prototyping

Example:

```ts
export interface ContextReplayResponse {
  data: {
    all: PandasDict;
    t_minus_60?: PandasDict;
    prev_day_business_hours?: PandasDict;
    m15?: PandasDict;
    h1?: PandasDict;
    [key: string]: any;  // flexible extension
  };
  metrics: {
    prev_day: PrevDayMetrics;
    [key: string]: any;  // in case you add more metrics later
  };
}
```

Now small backend changes won’t break your UI.

### But the real pro-move?

Export an **OpenAPI schema** from FastAPI and generate TypeScript types automatically.

You literally already have it:
FastAPI generates `/docs` and `/openapi.json`.

Then you run:

```
npx openapi-typescript http://localhost:8000/openapi.json --output src/lib/types/api.ts
```

Boom.
Frontend types update **by themselves** every time the backend changes.

Zero manual syncing.
Zero “why is this undefined?” moments.

Once your API stabilizes, you can tighten the types again, get strict, and enjoy that lovely TypeScript safety net.

If you want, I can help you:
• generate the OpenAPI file
• set up automatic TypeScript type generation
• or restructure your endpoint to be versioned so UI never breaks mid-refactor.

Your call.
