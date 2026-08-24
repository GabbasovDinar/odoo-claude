---
name: odoo-owl
description: Implement, debug, review, and migrate Odoo OWL/frontend code. Use for components, templates, services, registries, hooks, patches, assets, frontend tests, or OWL changes during an Odoo 16 to 18 migration.
---

# Odoo OWL and frontend

Use target Odoo source and existing project frontend code as the primary API reference.

## Workflow

1. Identify Odoo version and asset bundle.
2. Locate the upstream component/service/registry being extended.
3. Inspect target-version imports and signatures.
4. Confirm template name, component registration, and asset inclusion.
5. Implement the smallest supported extension.
6. Add frontend/unit/integration coverage where the project supports it.

## Rules

- Keep props/state ownership explicit.
- Use supported Odoo services/hooks instead of importing internal singletons casually.
- Clean up listeners/timers/subscriptions when required by lifecycle.
- Prefer registries/hooks over patching when a supported extension point exists.
- When patching, verify the exact target object/prototype and method signature.
- Keep JS/XML/SCSS in the correct manifest asset bundle.
- Ensure component template names match registrations.
- Validate QWeb/OWL selectors against target source.

## Migration discipline

For 16 -> 18, treat 16 -> 17 and 17 -> 18 separately. Do not rely on assumed OWL major-version labels; inspect target frontend code. Preserve behavior before refactoring component structure.

## Verification

Check browser behavior, console errors, asset loading, template registration, and relevant frontend tests. Do not claim runtime correctness from static inspection alone.
