const fs = require("fs");
const path = require("path");

function isPlainObject(value) {
    return value && typeof value === "object" && !Array.isArray(value);
}

function deepMerge(base, override) {
    const result = { ...base };
    for (const [key, value] of Object.entries(override)) {
        if (isPlainObject(value) && isPlainObject(result[key])) {
            result[key] = deepMerge(result[key], value);
        } else {
            result[key] = value;
        }
    }
    return result;
}

function loadJson(filePath) {
    if (!fs.existsSync(filePath)) return {};
    return JSON.parse(fs.readFileSync(filePath, "utf8"));
}

function ensureDir(dirPath) {
    fs.mkdirSync(dirPath, { recursive: true });
}

function mergeDirs(baseDir, overrideDir, outDir) {
    ensureDir(outDir);
    const baseFiles = fs.existsSync(baseDir) ? fs.readdirSync(baseDir) : [];
    const overrideFiles = fs.existsSync(overrideDir) ? fs.readdirSync(overrideDir) : [];
    const allFiles = new Set([...baseFiles, ...overrideFiles]);

    for (const file of allFiles) {
        if (!file.endsWith(".json")) continue;
        const basePath = path.join(baseDir, file);
        const overridePath = path.join(overrideDir, file);
        const outPath = path.join(outDir, file);

        const baseJson = loadJson(basePath);
        const overrideJson = loadJson(overridePath);
        const merged = deepMerge(baseJson, overrideJson);

        fs.writeFileSync(outPath, JSON.stringify(merged, null, 2));
    }
}

const [baseDir, overrideDir, outDir] = process.argv.slice(2);

if (!baseDir || !overrideDir || !outDir) {
    console.error("Usage: node merge-translations.js <baseDir> <overrideDir> <outDir>");
    process.exit(1);
}

mergeDirs(baseDir, overrideDir, outDir);
