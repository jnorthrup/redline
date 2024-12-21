function messageLoop() {
    // ...existing code...

    // Add 20 character model leftmost
    const model = "ModelName".padEnd(20, ' ');
    console.log(model + message);

    // Add tool legend
    const toolLegend = "Tool Legend: [T]ool1, [T]ool2, [T]ool3";
    console.log(toolLegend);

    // ...existing code...
}
