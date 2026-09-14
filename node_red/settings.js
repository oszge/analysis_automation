module.exports = {
    uiHost: "127.0.0.1",
    uiPort: 1880,
    flowFile: require("path").join(__dirname, "flows.json"),
    flowFilePretty: true,
    diagnostics: { enabled: false },
    runtimeState: { enabled: false },
    editorTheme: { projects: { enabled: false } },
    logging: { console: { level: "info", metrics: false, audit: false } }
};
