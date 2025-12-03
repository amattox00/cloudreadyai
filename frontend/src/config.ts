// src/config.ts
//
// Central place for frontend → backend URLs.
// We avoid using "localhost" so things work both locally and
// when you hit the dev server on an EC2 public IP.

const API_HOST =
  import.meta.env.VITE_API_HOST || window.location.hostname;

/**
 * Base URL for the FastAPI backend.
 *
 * - In EC2 dev:   http://3.151.80.236:3001 -> hostname is 3.151.80.236
 *   so this becomes http://3.151.80.236:8000
 * - In local dev: http://localhost:3000 -> hostname is localhost
 *   so this becomes http://localhost:8000
 */
const API_BASE =
  import.meta.env.VITE_API_BASE_URL || `http://${API_HOST}:8000`;

// Export with the old name (what pages currently import)
export { API_BASE };

// Also export a more explicit alias if we want it later
export const API_BASE_URL = API_BASE;

/**
 * Optional: frontend base URL (not strictly needed right now,
 * but handy if we ever build absolute links back to the app).
 */
export const FRONTEND_BASE_URL =
  import.meta.env.VITE_FRONTEND_BASE_URL || `http://${API_HOST}:3001`;
