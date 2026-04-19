/**
 * Event Aggregator Frontend
 * Vanilla JS with fetch API
 */

const API_BASE = '/api/v1';

// State
let currentPage = 1;
let totalPages = 1;
let currentFilters = {};

/**
 * Fetch events from API with optional filters
 * @param {Object} filters - Query parameters for filtering
 * @returns {Promise<Object>} - Events data with pagination
 */
async function fetchEvents(filters = {}) {
    try {
        const params = new URLSearchParams();
        
        if (filters.venue) params.append('venue', filters.venue);
        if (filters.dateFrom) params.append('date_from', filters.dateFrom);
        if (filters.dateTo) params.append('date_to', filters.dateTo);
        if (filters.page) params.append('page', filters.page);
        
        const queryString = params.toString() ? `?${params.toString()}` : '';
        const response = await fetch(`${API_BASE}/events${queryString}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Error fetching events:', error);
        showError('Failed to load events. Please try again later.');
        return null;
    }
}

/**
 * Fetch venues from API and populate dropdown
 */
async function fetchVenues() {
    try {
        const response = await fetch(`${API_BASE}/venues`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        populateVenueDropdown(data.venues || []);
    } catch (error) {
        console.error('Error fetching venues:', error);
    }
}

/**
 * Populate the venue dropdown with fetched venues
 * @param {Array} venues - List of venue objects
 */
function populateVenueDropdown(venues) {
    const select = document.getElementById('venue-filter');
    
    // Keep the "All Venues" option
    select.innerHTML = '<option value="">All Venues</option>';
    
    venues.forEach(venue => {
        const option = document.createElement('option');
        option.value = venue.id || venue.name;
        option.textContent = venue.name;
        select.appendChild(option);
    });
}

/**
 * Render events as cards in the events grid
 * @param {Array} events - List of event objects
 */
function renderEvents(events) {
    const grid = document.getElementById('events-grid');
    const countElement = document.getElementById('events-count');
    
    if (!events || events.length === 0) {
        grid.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <p>No events found</p>
            </div>
        `;
        countElement.textContent = '0 events found';
        return;
    }
    
    countElement.textContent = `${events.length} event${events.length !== 1 ? 's' : ''} found`;
    
    grid.innerHTML = events.map(event => `
        <article class="event-card">
            <h2 class="event-title">${escapeHtml(event.title)}</h2>
            <span class="event-venue">${escapeHtml(event.venue)}</span>
            <div class="event-meta">
                <div class="event-meta-item">
                    <span>📅</span>
                    <time>${formatDate(event.date)}</time>
                </div>
                <div class="event-meta-item">
                    <span>📍</span>
                    <span>${escapeHtml(event.location || 'Location TBA')}</span>
                </div>
                <div class="event-meta-item">
                    <span>💰</span>
                    <span>${event.price ? formatPrice(event.price) : 'Free'}</span>
                </div>
            </div>
        </article>
    `).join('');
}

/**
 * Show error message in the events grid
 * @param {string} message - Error message to display
 */
function showError(message) {
    const grid = document.getElementById('events-grid');
    const countElement = document.getElementById('events-count');
    
    grid.innerHTML = `
        <div class="error">
            <p>⚠️ ${escapeHtml(message)}</p>
        </div>
    `;
    countElement.textContent = 'Error loading events';
}

/**
 * Setup filter event listeners
 */
function setupFilters() {
    const venueSelect = document.getElementById('venue-filter');
    const dateFrom = document.getElementById('date-from');
    const dateTo = document.getElementById('date-to');
    const applyBtn = document.getElementById('apply-filters');
    const clearBtn = document.getElementById('clear-filters');
    
    // Apply filters button
    applyBtn.addEventListener('click', async () => {
        currentFilters = {
            venue: venueSelect.value,
            dateFrom: dateFrom.value,
            dateTo: dateTo.value,
            page: 1
        };
        currentPage = 1;
        await loadEvents();
    });
    
    // Clear filters button
    clearBtn.addEventListener('click', async () => {
        venueSelect.value = '';
        dateFrom.value = '';
        dateTo.value = '';
        currentFilters = {};
        currentPage = 1;
        await loadEvents();
    });
    
    // Allow Enter key to apply filters from inputs
    [dateFrom, dateTo].forEach(input => {
        input.addEventListener('keypress', async (e) => {
            if (e.key === 'Enter') {
                currentFilters = {
                    venue: venueSelect.value,
                    dateFrom: dateFrom.value,
                    dateTo: dateTo.value,
                    page: 1
                };
                currentPage = 1;
                await loadEvents();
            }
        });
    });
}

/**
 * Setup pagination controls
 */
function setupPagination() {
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    
    prevBtn.addEventListener('click', async () => {
        if (currentPage > 1) {
            currentPage--;
            currentFilters.page = currentPage;
            await loadEvents();
            scrollToTop();
        }
    });
    
    nextBtn.addEventListener('click', async () => {
        if (currentPage < totalPages) {
            currentPage++;
            currentFilters.page = currentPage;
            await loadEvents();
            scrollToTop();
        }
    });
}

/**
 * Update pagination UI state
 */
function updatePagination() {
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageInfo = document.getElementById('page-info');
    
    prevBtn.disabled = currentPage <= 1;
    nextBtn.disabled = currentPage >= totalPages;
    pageInfo.textContent = `Page ${currentPage} of ${totalPages}`;
}

/**
 * Load events and update UI
 */
async function loadEvents() {
    const grid = document.getElementById('events-grid');
    grid.innerHTML = '<div class="loading">Loading events...</div>';
    
    const data = await fetchEvents(currentFilters);
    
    if (data) {
        renderEvents(data.items || []);
        totalPages = data.total_pages || 1;
        currentPage = data.current_page || 1;
        updatePagination();
    }
}

/**
 * Scroll to top of events section
 */
function scrollToTop() {
    document.getElementById('events-grid').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Escape HTML special characters
 * @param {string} text - Text to escape
 * @returns {string} - Escaped text
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Format date for display
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted date
 */
function formatDate(dateString) {
    if (!dateString) return 'Date TBA';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Format price for display
 * @param {number|string} price - Price value
 * @returns {string} - Formatted price
 */
function formatPrice(price) {
    const numPrice = typeof price === 'string' ? parseFloat(price) : price;
    if (isNaN(numPrice) || numPrice === 0) return 'Free';
    return `$${numPrice.toFixed(2)}`;
}

/**
 * Initialize the application
 */
async function init() {
    // Load venues first
    await fetchVenues();
    
    // Setup event listeners
    setupFilters();
    setupPagination();
    
    // Load initial events
    await loadEvents();
}

// Start the app when DOM is ready
document.addEventListener('DOMContentLoaded', init);
