================================================================================
                           ANTIPODE AIRLINES
                  Client-Side Flight Path & Projection Viewer
================================================================================

1. OVERVIEW & PROJECT PHILOSOPHY
--------------------------------------------------------------------------------
Antipode Airlines is a lightweight, zero-dependency, web-based visualization tool 
designed to calculate and map multi-leg flight connections to exact geographical 
antipodes using real-world open aviation data. 

The core mission of the project is to determine the most viable flight route 
from any user-specified origin airport to the closest operational airport 
located near the exact antipodal point on Earth (the point diametrically opposite 
it on the globe).

Built purely with vanilla HTML5, CSS3, JavaScript (ES6+), and lightweight D3.js 
spatial projection libraries, Antipode Airlines operates completely client-side. 
It requires no backend server code, database setup, or complex build tooling. 
All graph traversal, spatial distance metrics, and vector rendering happen directly 
within the browser session.


2. CORE ARCHITECTURE & SYSTEM COMPONENTS
--------------------------------------------------------------------------------
The codebase is structured into a single, cohesive file system that orchestrates 
data parsing, graph search algorithms, UI state management, and SVG rendering.

A. User Interface Layout & Layout Engine
   - 2/5th (40%) Left Sidebar: Houses controls, user query inputs, route metrics, 
     and the detailed itinerary list.
   - 3/5th (60%) Viewport: Houses the interactive D3.js-driven Robinson projection 
     map container.
   - Fixed Top Header: Displays the brand identity and global system state.

B. Data Parsing & Graph Construction Engine (FlightEngine Class)
   - Airports Processor: Loads and parses OpenFlights `airports.dat` CSV data. 
     Extracts IATA/ICAO identifiers, airport names, locations (city/country), 
     and converts geographical coordinates (Latitude/Longitude) into 3D unit 
     vector cartesian coordinates (x, y, z) for instant, low-overhead spherical 
     distance comparisons.
   - Routes Processor: Loads and parses OpenFlights `routes.dat` CSV data. 
     Constructs an adjacency list (`adjList`) mapping every source airport to 
     a set of direct destination airport nodes.
   - Candidate Ranking Module: Calculates the exact spatial antipode of the 
     selected origin point (negating latitude and shifting longitude by 180 degrees). 
     Ranks all global airports based on Euclidean distance in 3D cartesian space 
     to isolate the top 20 candidate target airports closest to the theoretical antipode.
   - Breadth-First Search (BFS) Routing Engine: Executes an unweighted shortest-path 
     graph traversal across the flight network from the origin airport to candidate 
     antipodal destinations, picking the route with the fewest transfers/legs.

C. Vector Map Renderer (MapRenderer Class)
   - Robinson Projection Model: Built using `d3-geo` and `d3-geo-projection`. 
     Renders the globe using the Robinson projection format to maintain visually 
     balanced landmass shapes and equal-area trade-offs.
   - Dynamic Layout Scaling: Measures the target SVG viewport dimensions and dynamically 
     recalculates bounding boxes using `.fitExtent()` to ensure the map fills the space.
   - TopoJSON Land Mass Loader: Fetches land vectors from world-atlas 110m resolution data, 
     rendering land geometries, spherical boundaries, and graticule reference grids.
   - Great-Circle Arc Overlay: Draws geodesic paths connecting each leg in the computed 
     route using `LineString` GeoJSON objects mapped through D3's geoPath generator.
   - Visual Marker System: Highlights exact target antipodes with dashed indicator rings, 
     origin airports in distinct accent colors (orange), and destination nodes in 
     cyan vector markers with contextual text labels.


3. DETAILED FEATURE BREAKDOWN
--------------------------------------------------------------------------------
- Real-Time Search Panel:
  - Input field supporting both 3-letter IATA codes (e.g., SYD, JFK, LHR) and 4-letter 
    ICAO codes (e.g., YSSY, KJFK, EGLL).
  - Equalized action trigger button ("Compute Route") aligned flush with the input box.
  - Live system status messages tracking dat file load progress and search execution alerts.

- Flight Metrics Panel:
  - Selected Origin Airport & City.
  - Theoretical Antipode Coordinates (Exact Latitude and Longitude).
  - Nearest Connected Destination Airport & City.
  - Total Leg Count (number of individual flights required).

- Itinerary Breakdown:
  - Sequential leg-by-leg listing of each flight segment.
  - Formatted leg indicators detailing origin node to destination node transition.

- Robinson Projection Map Display:
  - High-performance vector canvas rendering.
  - Automatic re-projection on viewport/browser window resize.
  - Clear color coding for flight paths, airport nodes, exact antipode targets, and 
    geographical terrain.


4. DATA SOURCES & FORMAT REQUIREMENTS
--------------------------------------------------------------------------------
To function correctly, the browser application expects two data files located in the 
same working directory as `index.html`:

1. `airports.dat`
   - Source: OpenFlights Airport Database
   - Format: CSV / Dat file
   - Expected Fields: Airport ID, Name, City, Country, IATA, ICAO, Latitude, Longitude, 
     Altitude, Timezone, DST, Tz database time zone, Type, Source.

2. `routes.dat`
   - Source: OpenFlights Route Database
   - Format: CSV / Dat file
   - Expected Fields: Airline, Airline ID, Source airport, Source airport ID, 
     Destination airport, Destination airport ID, Codeshare, Stops, Equipment.

3. World Atlas TopoJSON (Loaded via CDN fallback):
   - URL: `https://cdn.jsdelivr.net/npm/world-atlas@2/land-110m.json`
   - Provides global shoreline vector boundaries.


5. HOSTING & DEPLOYMENT INSTRUCTIONS
--------------------------------------------------------------------------------
Because Antipode Airlines is pure static HTML/CSS/JS, it can be hosted on virtually 
any web server or static site hosting service without needing Node.js, Python, PHP, 
or backend databases.

Option A: Local Development Server
Due to browser CORS (Cross-Origin Resource Sharing) security restrictions when 
fetching local dataset files (`airports.dat`, `routes.dat`), you must serve the 
files via HTTP/HTTPS rather than double-clicking the HTML file directly (`file://`).

1. Using Python 3:
   Open a terminal in the project directory and run:
   $ python3 -m http.server 8000
   Then open your browser and navigate to: http://localhost:8000

2. Using Node.js (`npx http-server` or `serve`):
   $ npx serve .
   Or:
   $ npx http-server -p 8000

3. Using Caddy:
   $ caddy file-server --listen :8000

Option B: Deployment to Static Hosting Services

- GitHub Pages:
  1. Push `index.html`, `airports.dat`, and `routes.dat` to a GitHub repository.
  2. Navigate to Repository Settings -> Pages.
  3. Select the `main` or `master` branch as the build source and save.
  4. Your site will be live at `https://<username>.github.io/<repository-name>/`.

- Cloudflare Pages:
  1. Connect your git repository to Cloudflare Pages.
  2. Set the Build Command to empty/none.
  3. Set the Output Directory to `/` (root).
  4. Click "Save and Deploy".

- Netlify / Vercel:
  1. Drag and drop the directory containing `index.html`, `airports.dat`, and `routes.dat` 
     into the Netlify/Vercel deployment console.
  2. Alternatively, connect your repository and set the publish directory to root (`.`).


6. BROWSER COMPATIBILITY & PERFORMANCE
--------------------------------------------------------------------------------
- Compatible Browsers: Modern versions of Chrome, Firefox, Safari, Edge, and Opera.
- Memory & Performance: Parsing the dataset (~8,000 airports and ~67,000 routes) 
  takes approximately 150ms to 400ms on modern CPU hardware upon initial page load.
- Graph Search Efficiency: BFS traversal across the dataset completes in < 15ms.


7. LICENSE & ACKNOWLEDGMENTS
--------------------------------------------------------------------------------
- Airport and route data provided by OpenFlights.org under the Open Database License.
- Map boundaries provided by Natural Earth and TopoJSON/World-Atlas.
- Projection math powered by D3.js (d3-geo and d3-geo-projection).
================================================================================