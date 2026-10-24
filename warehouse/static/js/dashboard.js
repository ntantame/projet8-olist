const API_URL = "http://127.0.0.1:8000/api";
const TOKEN = "89395cd4c3bffbf12d8c9f045d449f50da123788";
const HEADERS = { "Authorization": `Token ${TOKEN}`, "Content-Type": "application/json" };

let chartCA, chartCat, chartLivraison, chartSatisfaction;

// --- CHARGEMENT DYNAMIQUE DES FILTRES ---
function loadFilterOptions() {
    // 1. Régions
    fetch(`${API_URL}/livraison/par-region/`, { headers: HEADERS })
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById('filter-region');
            const sortedData = data.sort((a, b) => a.etat.localeCompare(b.etat));
            sortedData.forEach(item => {
                const option = document.createElement('option');
                option.value = item.etat;
                option.text = item.etat;
                select.appendChild(option);
            });
        });

    // 2. Catégories
    fetch(`${API_URL}/ventes/par-categorie/`, { headers: HEADERS })
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById('filter-categorie');
            data.forEach(item => {
                if(item.categorie && item.categorie !== 'inconnue') {
                    const option = document.createElement('option');
                    option.value = item.categorie;
                    option.text = item.categorie;
                    select.appendChild(option);
                }
            });
        });

    // 3. Villes (Liste prédéfinie)
    const villesBresil = ["sao paulo", "rio de janeiro", "brasilia", "salvador", "fortaleza", "belo horizonte", "manaus", "curitiba", "recife", "porto alegre"];
    const datalist = document.getElementById('villes-list');
    villesBresil.forEach(ville => {
        const option = document.createElement('option');
        option.value = ville;
        datalist.appendChild(option);
    });
}

// --- CHARGEMENT DES DONNÉES ---
function loadAllData() {
    const dateDebut = document.getElementById('filter-date-debut').value;
    const dateFin = document.getElementById('filter-date-fin').value;
    const region = document.getElementById('filter-region').value;
    const categorie = document.getElementById('filter-categorie').value;
    const ville = document.getElementById('filter-ville').value;

    let queryParams = new URLSearchParams();
    if (dateDebut) queryParams.append("date_debut", dateDebut);
    if (dateFin) queryParams.append("date_fin", dateFin);
    if (region) queryParams.append("region", region);
    if (categorie) queryParams.append("categorie", categorie);
    if (ville) queryParams.append("ville", ville);

    const queryString = queryParams.toString() ? `?${queryParams.toString()}` : "";

    // KPIs
    fetch(`${API_URL}/kpis/resume/${queryString}`, { headers: HEADERS })
        .then(res => res.json())
        .then(data => {
            document.getElementById('kpi-ca').innerText = (data.CA_total / 1000000).toFixed(2) + " M R$";
            document.getElementById('kpi-cmd').innerText = data.total_commandes.toLocaleString('fr-FR');
            document.getElementById('kpi-delai').innerText = data.delai_moyen + " j";
            document.getElementById('kpi-retard').innerText = data.taux_retard + " %";
            document.getElementById('kpi-note').innerText = data.score_moyen + "/5";
        });

    // Graphique CA
    fetch(`${API_URL}/ventes/par-periode/${queryString}`, { headers: HEADERS })
        .then(res => res.json())
        .then(data => {
            if (chartCA) chartCA.destroy();
            chartCA = new Chart(document.getElementById('chartCA'), {
                type: 'line', data: { labels: data.map(d => d.periode), datasets: [{ label: 'CA (R$)', data: data.map(d => d.CA), borderColor: '#008080', backgroundColor: 'rgba(0, 128, 128, 0.1)', fill: true, tension: 0.3 }] }
            });
        });

    // Graphique Catégories
    fetch(`${API_URL}/ventes/par-categorie/${queryString}`, { headers: HEADERS })
        .then(res => res.json())
        .then(data => {
            if (chartCat) chartCat.destroy();
            const top5 = data.slice(0, 5);
            chartCat = new Chart(document.getElementById('chartCat'), {
                type: 'bar', data: { labels: top5.map(d => d.categorie), datasets: [{ label: 'CA (R$)', data: top5.map(d => d.chiffre_affaires), backgroundColor: '#4DB6AC' }] }, options: { indexAxis: 'y' }
            });
        });

    // Graphique Livraison
    fetch(`${API_URL}/livraison/par-region/${queryString}`, { headers: HEADERS })
        .then(res => res.json())
        .then(data => {
            if (chartLivraison) chartLivraison.destroy();
            chartLivraison = new Chart(document.getElementById('chartLivraison'), {
                type: 'bar', data: { labels: data.map(d => d.etat), datasets: [{ label: 'Délai (j)', data: data.map(d => d.delai_moyen_jours), backgroundColor: '#008080' }, { label: 'Retard (%)', data: data.map(d => d.taux_retard_pourcentage), backgroundColor: '#4DB6AC' }] }
            });
        });

    // Graphique Satisfaction
    fetch(`${API_URL}/satisfaction/par-region/${queryString}`, { headers: HEADERS })
        .then(res => res.json())
        .then(data => {
            if (chartSatisfaction) chartSatisfaction.destroy();
            chartSatisfaction = new Chart(document.getElementById('chartSatisfaction'), {
                type: 'bar', data: { labels: data.map(d => d.etat), datasets: [{ label: 'Note / 5', data: data.map(d => d.note_moyenne), backgroundColor: '#4DB6AC' }] }, options: { scales: { y: { min: 0, max: 5 } } }
            });
        });
}

// Initialisation
window.onload = () => {
    loadFilterOptions();
    loadAllData();
};