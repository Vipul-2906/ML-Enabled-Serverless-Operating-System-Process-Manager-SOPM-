let processes = [
    {name: "process1", status: "Running", cpu: 35, memory: 120},
    {name: "process2", status: "Stopped", cpu: 0, memory: 0},
    {name: "process3", status: "Running", cpu: 55, memory: 200}
];

function renderTable() {
    const tbody = document.querySelector("#processTable tbody");
    tbody.innerHTML = "";

    processes.forEach((p, index) => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${p.name}</td>
            <td class="${p.status === "Running" ? "status-running" : "status-stopped"}">
                ${p.status}
            </td>
            <td>
                <div class="progress-bar">
                    <div class="progress cpu-bar" style="width: ${p.cpu}%"></div>
                </div>
                ${p.cpu}%
            </td>
            <td>
                <div class="progress-bar">
                    <div class="progress memory-bar" style="width: ${p.memory/2}px"></div>
                </div>
                ${p.memory}MB
            </td>
            <td>
                ${p.status === "Running" ? 
                    `<button class="stop" onclick="stopProcess(${index})">Stop</button>` : 
                    `<button class="start" onclick="startProcess(${index})">Start</button>`}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

function startProcess(index) {
    processes[index].status = "Running";
    processes[index].cpu = Math.floor(Math.random() * 50) + 10; // random simulated usage
    processes[index].memory = Math.floor(Math.random() * 200) + 50;
    renderTable();
}

function stopProcess(index) {
    processes[index].status = "Stopped";
    processes[index].cpu = 0;
    processes[index].memory = 0;
    renderTable();
}

// Initial render
renderTable();
