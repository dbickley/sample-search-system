const submitButton = document.getElementById('submit-button');
const reindexButton = document.getElementById('reindex-btn');
const updateEmbeddingsButton = document.getElementById('update-embeddings-btn');
const resultDiv = document.getElementById('result');
const userQueryInput = document.getElementById('user-query');
const mainCategorySelect = document.getElementById('main-category');
const subCategorySelect = document.getElementById('sub-category');
const numberOfResultsSelect = document.getElementById('number-of-results');
const prevPageButton = document.getElementById('prev-page');
const nextPageButton = document.getElementById('next-page');
const pageNumberSpan = document.getElementById('page-number');
const facetOptionsDiv = document.getElementById('facet-options');
const predictTaxonomyCheckbox = document.getElementById('predict-taxonomy');
const keywordSearchCheckbox = document.getElementById('keyword-search');
const vectorSearchCheckbox = document.getElementById('vector-search');
const reRankCheckbox = document.getElementById('re-rank');

// Experiment tab elements
const experimentQueryInput1 = document.getElementById('experiment-query1');
const experimentQueryInput2 = document.getElementById('experiment-query2');
const experimentSubmitButton1 = document.getElementById('experiment-submit1');
const experimentSubmitButton2 = document.getElementById('experiment-submit2');
const experimentResultDiv1 = document.getElementById('experiment-result1');
const experimentResultDiv2 = document.getElementById('experiment-result2');
const experimentSubmitButton = document.getElementById('experiment-submit');
const resultDiv1 = document.getElementById('experiment-result1');
const resultDiv2 = document.getElementById('experiment-result2');



let facets = {};
let currentPage = 1;
let totalResults = 0;
let allowedFacets = [];
let experimentResults1 = null; // Store results for experiment comparison


userQueryInput.addEventListener('keyup', function (event) {
    if (event.key === 'Enter') {
        submitButton.click();
    }
});

submitButton.addEventListener('click', () => {
    currentPage = 1;
    fetchResults();
});

prevPageButton.addEventListener('click', () => {
    if (currentPage > 1) {
        currentPage--;
        fetchResults();
    }
});

nextPageButton.addEventListener('click', () => {
    const totalPages = Math.ceil(totalResults / parseInt(numberOfResultsSelect.value, 10));
    if (currentPage < totalPages) {
        currentPage++;
        fetchResults();
    }
});

experimentSubmitButton.addEventListener('click', () => {
    const query1 = experimentQueryInput1.value;
    const query2 = experimentQueryInput2.value;
    fetchExperimentResults(query1, query2);
});

function openTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(tab => tab.classList.remove('active'));
    document.getElementById(tabId).classList.add('active');
    document.querySelector(`button[onclick="openTab('${tabId}')"]`).classList.add('active');

    if (tabId === 'experiment-tab') {
        document.getElementById('experiment-result1').innerHTML = '';
        document.getElementById('experiment-result2').innerHTML = '';
        experimentResults1 = null; // Clear previous results
    }
}


function addFacet() {
    const field = document.getElementById('facet-field').value;
    const value = document.getElementById('facet-value').value;
    if (field && value) {
        if (facets[field]) {
            if (Array.isArray(facets[field])) {
                facets[field].push(value);
            } else {
                facets[field] = [facets[field], value];
            }
        } else {
            facets[field] = value;
        }
        console.log("Facets updated:", facets);
        document.getElementById('facet-field').value = '';
        document.getElementById('facet-value').value = '';
        renderFacets();
    }
}


async function fetchCategories() {
    const response = await fetch('/api/categories');
    const categories = await response.json();

    mainCategorySelect.innerHTML = '<option value="">All Main Categories</option>';
    subCategorySelect.innerHTML = '<option value="">All Sub Categories</option>';

    categories.main_categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.text = cat;
        mainCategorySelect.appendChild(option);
    });

    categories.sub_categories.forEach(cat => {
        const option = document.createElement('option');
        option.value = cat;
        option.text = cat;
        subCategorySelect.appendChild(option);
    });
}

function renderFacets() {
    facetOptionsDiv.innerHTML = '';
    if (Object.keys(facets).length === 0) {
        facetOptionsDiv.innerHTML = '<p>No facets selected.</p>';
        return;
    }

    for (const field in facets) {
        const value = facets[field];
        const facetValue = Array.isArray(value) ? value.join(', ') : value;
        const facetDiv = document.createElement('div');
        facetDiv.className = 'facet-option';
        facetDiv.textContent = `${field}: ${facetValue}`;
        facetOptionsDiv.appendChild(facetDiv);
    }
}
async function fetchResults() {
    const query = document.getElementById('user-query').value;
    const mainCategory = mainCategorySelect.value || null;
    const subCategory = subCategorySelect.value || null;
    const numberOfResults = parseInt(numberOfResultsSelect.value, 10);
    const startIndex = (currentPage - 1) * numberOfResults;
    const predictTaxonomy = predictTaxonomyCheckbox.checked;
    const keywordSearch = keywordSearchCheckbox.checked;
    const vectorSearch = vectorSearchCheckbox.checked;
    const reRank = reRankCheckbox.checked;

    const userQuery = {
        query: query,
        facets: facets,
        main_category: mainCategory,
        sub_category: subCategory,
        number_of_results: numberOfResults,
        start_index: startIndex,
        predict_taxonomy: predictTaxonomy,
        keyword_search: keywordSearch,
        vector_search: vectorSearch,
        re_rank: reRank
    };
    console.log('fetchResults');
    console.log(JSON.stringify(userQuery));
    const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userQuery),
    });
    const data = await response.json();

    resultDiv.innerHTML = '';
    totalResults = data.number_of_results;
    pageNumberSpan.textContent = currentPage;

    if (!data || !data.search_result_rows || data.search_result_rows.length === 0) {
        resultDiv.innerHTML = "<p>No results found.</p>";
        return;
    }

    allowedFacets = data.allowed_facets || [];

    data.search_result_rows.forEach(result => {
        const card = document.createElement('div');
        card.className = 'result-card';

        const imageUrl = result.image_url || 'placeholder_image.jpg';
        const title = result.title || 'No Title Available';
        const mainCategory = result.main_category || 'N/A';
        const subCategory = result.sub_category || 'N/A';
        const score = result.score || 'N/A';
        const rank = result.orginal_rank !== undefined ? result.orginal_rank + 1 : 'N/A';
        const rerank = result.rerank !== undefined ? result.rerank + 1 : 'N/A';
        const ratings = result.ratings || '0';
        const noOfRatings = result.no_of_ratings || '0';
        const discountPrice = result.discount_price || 'N/A';
        const actualPrice = result.actual_price || 'N/A';
        const productUrl = result.product_url || '#';

        card.innerHTML = `
            <img src="${imageUrl}" alt="${title}">
            <div class="result-card-content">
                <h3>${title}</h3>
                <p><strong>Category:</strong> ${mainCategory} > ${subCategory}</p>
                <p><strong>Price:</strong> ${discountPrice} <del>${actualPrice}</del></p>
                <a href="${productUrl}" target="_blank">View Product</a>
            </div>
            <div class="result-card-stats">
                <p><strong>Ratings:</strong> ${ratings} (${noOfRatings} reviews)</p>
                <p><strong>Score:</strong> ${score}</p>
                <p><strong>Rank:</strong> ${rank}</p>
                <p><strong>Rerank:</strong> ${rerank}</p>
            </div>
        `;

        resultDiv.appendChild(card);
    });
}
async function fetchExperimentResults(query1, query2) {
    const numberOfResults = parseInt(document.getElementById('number-of-results').value, 10);
    
    const predictTaxonomy1 = document.getElementById('predict-taxonomy1').checked;
    const keywordSearch1 = document.getElementById('keyword-search1').checked;
    const vectorSearch1 = document.getElementById('vector-search1').checked;
    const reRank1 = document.getElementById('re-rank1').checked;
    const fieldsToMatch1 = document.getElementById('fields-to-match1').value.split(',');
    const keywordBoost1 = parseFloat(document.getElementById('keyword-boost1').value);
    const phraseBoost1 = parseFloat(document.getElementById('phrase-boost1').value);
    const phrasePrefixBoost1 = parseFloat(document.getElementById('phrase-prefix-boost1').value);
    const fuzzyBoost1 = parseFloat(document.getElementById('fuzzy-boost1').value);
    const bestFieldsBoost1 = parseFloat(document.getElementById('best-fields-boost1').value);
    const predictedCategoryBoost1 = parseFloat(document.getElementById('predicted-category-boost1').value);
    const vectorK1 = parseInt(document.getElementById('vector-k1').value);
    const vectorCandidates1 = parseInt(document.getElementById('vector-candidates1').value);
    const vectorBoost1 = parseFloat(document.getElementById('vector-boost1').value);

    const predictTaxonomy2 = document.getElementById('predict-taxonomy2').checked;
    const keywordSearch2 = document.getElementById('keyword-search2').checked;
    const vectorSearch2 = document.getElementById('vector-search2').checked;
    const reRank2 = document.getElementById('re-rank2').checked;
    const fieldsToMatch2 = document.getElementById('fields-to-match2').value.split(',');
    const keywordBoost2 = parseFloat(document.getElementById('keyword-boost2').value);
    const phraseBoost2 = parseFloat(document.getElementById('phrase-boost2').value);
    const phrasePrefixBoost2 = parseFloat(document.getElementById('phrase-prefix-boost2').value);
    const fuzzyBoost2 = parseFloat(document.getElementById('fuzzy-boost2').value);
    const bestFieldsBoost2 = parseFloat(document.getElementById('best-fields-boost2').value);
    const predictedCategoryBoost2 = parseFloat(document.getElementById('predicted-category-boost2').value);
    const vectorK2 = parseInt(document.getElementById('vector-k2').value);
    const vectorCandidates2 = parseInt(document.getElementById('vector-candidates2').value);
    const vectorBoost2 = parseFloat(document.getElementById('vector-boost2').value);
 
    const userQuery1 = {
        query: query1,
        number_of_results: numberOfResults,
        predict_taxonomy: predictTaxonomy1,
        keyword_search: keywordSearch1,
        vector_search: vectorSearch1,
        re_rank: reRank1,
        search_stratagy_verions: "v1",
        search_config: {
            fields_to_match: fieldsToMatch1,
            keyword: {
                boost: keywordBoost1,
                match_types: {
                    phrase: phraseBoost1,
                    phrase_prefix: phrasePrefixBoost1,
                    fuzzy: fuzzyBoost1,
                    best_fields: bestFieldsBoost1
                },
                predicted_category_boost: predictedCategoryBoost1
            },
            vector: {
                k: vectorK1,
                num_candidates: vectorCandidates1,
                boost: vectorBoost1,
                enabled: vectorSearch1
            }
        }
    };

    const userQuery2 = {
        ...userQuery1,
        query: query2,
        predict_taxonomy: predictTaxonomy2,
        keyword_search: keywordSearch2,
        vector_search: vectorSearch2,
        re_rank: reRank2,
        search_config: {
            fields_to_match: fieldsToMatch2,
            keyword: {
                boost: keywordBoost2,
                match_types: {
                    phrase: phraseBoost2,
                    phrase_prefix: phrasePrefixBoost2,
                    fuzzy: fuzzyBoost2,
                    best_fields: bestFieldsBoost2
                },
                predicted_category_boost: predictedCategoryBoost2
            },
            vector: {
                k: vectorK2,
                num_candidates: vectorCandidates2,
                boost: vectorBoost2,
                enabled: vectorSearch2
            }
        }
    };
    
    try {
        const response1 = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userQuery1),
        });
        const data1 = await response1.json();
        
        const response2 = await fetch('/api/search', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(userQuery2),
        });
        const data2 = await response2.json();
        
        renderExperimentResults(data1, data2);
    } catch (error) {
        console.error("Error fetching experiment results:", error);
    }
}

function renderExperimentResults(data1, data2) {
    const resultDiv1 = document.getElementById('experiment-result1');
    const resultDiv2 = document.getElementById('experiment-result2');

    resultDiv1.innerHTML = '';
    resultDiv2.innerHTML = '';

    const productRanks = new Map(); // Store ranks for both queries

    // Populate productRanks with data from both queries
    data1.search_result_rows.forEach((result, index) => {
        productRanks.set(result.product_id, { 1: index + 1 }); // Store rank for query 1
    });

    data2.search_result_rows.forEach((result, index) => {
        if (productRanks.has(result.product_id)) {
            productRanks.get(result.product_id)[2] = index + 1; // Add rank for query 2
        } else {
            productRanks.set(result.product_id, { 2: index + 1 }); // Product only in query 2
        }
    });

    // Render results, using productRanks for rank information
    data1.search_result_rows.forEach((result) => {
        const card = createExperimentResultCard(result, productRanks.get(result.product_id));
        resultDiv1.appendChild(card);
    });

    data2.search_result_rows.forEach((result) => {
        const card = createExperimentResultCard(result, productRanks.get(result.product_id));
        resultDiv2.appendChild(card);
    });
}

function createExperimentResultCard(result, ranks) {
    const card = document.createElement('div');
    card.className = 'result-card';

    const imageUrl = result.image_url || 'placeholder_image.jpg';
    const title = result.title || 'No Title Available';
    const mainCategory = result.main_category || 'N/A';
    const subCategory = result.sub_category || 'N/A';
    const score = result.score || 'N/A';
    const ratings = result.ratings || '0';
    const noOfRatings = result.no_of_ratings || '0';
    const discountPrice = result.discount_price || 'N/A';
    const actualPrice = result.actual_price || 'N/A';
    const productUrl = result.product_url || '#';
    const productId = result.product_id;

    const rank1 = ranks ? ranks[1] : null;
    const rank2 = ranks ? ranks[2] : null;

    card.innerHTML = `
        <img src="${imageUrl}" alt="${title}">
        <div class="result-card-content">
            <h3>${title}</h3>
            <p><strong>Category:</strong> ${mainCategory} > ${subCategory}</p>
            <p><strong>Price:</strong> ${discountPrice} <del>${actualPrice}</del></p>
            <a href="${productUrl}" target="_blank">View Product</a>
        </div>
        <div class="result-card-stats">
            <p><strong>Ratings:</strong> ${ratings} (${noOfRatings} reviews)</p>
            <p><strong>Score:</strong> ${score}</p>
            <p><strong>Query 1 Rank:</strong> ${rank1 || "N/A"}</p>
            <p><strong>Query 2 Rank:</strong> ${rank2 || "N/A"}</p>
            <p><strong>Original Rank:</strong> ${result.orginal_rank + 1 || "N/A"}</p>
        </div>
    `;

    if (rank1 && rank2 && rank1 !== rank2) {
        card.classList.add('rank-different');
    } else if (!rank1 || !rank2) { // If either is missing.
        card.classList.add('not-in-results');
    }

    return card;
}

resultDiv1.addEventListener('scroll', () => {
    resultDiv2.scrollTop = resultDiv1.scrollTop;
    resultDiv2.scrollLeft = resultDiv1.scrollLeft; // Optional: Synchronize horizontal scroll too
  });
  
  resultDiv2.addEventListener('scroll', () => {
    resultDiv1.scrollTop = resultDiv2.scrollTop;
    resultDiv1.scrollLeft = resultDiv2.scrollLeft; // Optional: Synchronize horizontal scroll too
  });
  
reindexButton.addEventListener('click', async () => {
    const response = await fetch('/api/reindex', { method: 'POST' });
    const message = await response.text();
    console.log(message);
});

updateEmbeddingsButton.addEventListener('click', async () => {
    const response = await fetch('/api/update_embeddings', { method: 'POST' });
    const message = await response.text();
    console.log(message);
});

document.addEventListener('DOMContentLoaded', () => {
    fetchResults(); // Perform blank search on page load
    fetchCategories(); // Fetch categories on page load
});

