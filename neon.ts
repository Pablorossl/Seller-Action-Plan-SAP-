import { defineConfig } from "@neon/config/v1";

export default defineConfig({
  // Postgres está incluido en cada rama. Django usa psycopg y DATABASE_URL;
  // las migraciones manuales usan DATABASE_URL_UNPOOLED. El login sigue en Django.
  auth: false,
  // Branch policy: per-branch tuning
  branch: (branch) => {
    if (branch.isDefault) {
      // Default branch: no overrides, uses project defaults
      return {};
    }
    if (!branch.exists) {
      // New non-default branches: auto-expire
      // Run `neon checkout <name>` to create a new branch with these settings
      return { ttl: "7d" };
    }
    // Existing branch: no changes
    return {};
  },
});
