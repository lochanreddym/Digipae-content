import { Config } from "@remotion/cli/config";

Config.setPublicDir("assets");
// Cloud sessions can't download Remotion's own Chrome; use the preinstalled headless shell when present.
if (process.env.REMOTION_BROWSER_EXECUTABLE) {
  Config.setBrowserExecutable(process.env.REMOTION_BROWSER_EXECUTABLE);
}
