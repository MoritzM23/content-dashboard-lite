import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    // Persistent FileSystem-Cache fuer Turbopack — entkoppelt die hochfrequenten
    // mmap-Reads aus node_modules. Verhindert das macOS-APFS "Resource deadlock
    // avoided (os error 11)" das den Dev-Server sonst regelmaessig in 500-State
    // versetzt.
    turbopackFileSystemCacheForDev: true,
  },
};

export default nextConfig;
