document.getElementById("submitBtn").addEventListener("click", () => {
    const formData = {
        weight: document.getElementById("weight").value,
        weight_unit: document.getElementById("weight_unit").value,
        height: document.getElementById("height").value,
        height_unit: document.getElementById("height_unit").value,
        age: document.getElementById("age").value,
        sex: document.getElementById("sex").value,
        activityLevel: document.getElementById("activityLevel").value,
    };

    fetch("/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(formData)
    })
    .then(response => response.json())
    .then(data => populateResultsTable(data))
    .catch(error => console.error('Error:', error));
});

function populateResultsTable(data) {
    const tableHeader = document.getElementById("resultsTableHeader");
    const tableBody = document.getElementById("resultsTableBody");

    // Clear existing table data
    tableHeader.innerHTML = "";
    tableBody.innerHTML = "";

    // Create table headers
    const headers = Object.keys(data[0]);
    headers.forEach(header => {
        const th = document.createElement("th");
        th.textContent = header;
        tableHeader.appendChild(th);
    });

    // Create table rows
    data.forEach(row => {
        const tr = document.createElement("tr");
        headers.forEach(header => {
            const td = document.createElement("td");
            td.textContent = row[header];
            tr.appendChild(td);
        });
        tableBody.appendChild(tr);
    });
}
