# Post-Migration Infrastructure Work

## Replace the temporary R2 development endpoint

The migration temporarily accepts Cloudflare's `r2.dev` public endpoint even
though Cloudflare documents it as intended for non-production use.

After the podcast migration is stable:

1. Configure a dedicated custom domain for the R2 bucket.
2. Validate TLS, `audio/mpeg`, content length, caching, and byte-range support.
3. Update enclosure URLs only with a controlled compatibility plan. Existing
   episode GUIDs must not change.
4. Run the full feed validator and playback tests.
5. Keep the old R2 URLs available long enough for podcast application caches.

This task is intentionally deferred so the hosting-domain change does not occur
during the Podbean directory migration.
