// Configuration
const API_URL = 'https://your-render-app-name.onrender.com'; // Replace with your actual Render URL

// Fetch menu items from the backend
async function fetchMenu() {
    try {
        const response = await fetch(`${API_URL}/api/menu`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        renderMenu(data);
    } catch (error) {
        console.error('Could not fetch menu:', error);
    }
}

// Render menu items to the webpage
function renderMenu(items) {
    const container = document.getElementById('menu-container');
    if (!container) return;
    
    container.innerHTML = ''; // Clear current content
    
    items.forEach(item => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'menu-item';
        itemDiv.innerHTML = `
            <h3>${item.name}</h3>
            <p>${item.description}</p>
            <p>Price: ${item.price} €</p>
        `;
        container.appendChild(itemDiv);
    });
}

// Run fetch on page load
document.addEventListener('DOMContentLoaded', fetchMenu);