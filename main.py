import aiohttp
import asyncio
from typing import List, Any, Dict
from pydantic import BaseModel
from bs4 import BeautifulSoup, SoupStrainer
import geopandas as gpd
from shapely.geometry import Point
from tqdm.asyncio import tqdm


class Site(BaseModel):
    drupal_id: str
    name: str
    lat: float
    long: float
    website: str = ""

    def generate_url(self) -> None:
        """Constructs the URL for the site using the drupal_id."""
        self.website = f"https://camping.se/node/{self.drupal_id}"


class CampingList(BaseModel):
    sites: List[Site] = list()
    items: List[Any] = list()
    headers: Dict[Any,Any] = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'sv-SE,sv;q=0.8,en-US;q=0.5,en;q=0.3',
        'X-Requested-With': 'XMLHttpRequest',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Referer': 'https://camping.se/sv/sok-och-boka',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
    }

    @staticmethod
    async def fetch_item_page(session, url, headers):
        async with session.get(url, headers=headers) as response:
            return await response.text()

    async def fetch_list_of_sites(self):
        base_url = 'https://camping.se/sv/api/cbis-product-list'
        params = {
            'nodeId': '679',
            'facilityGroupsOperatorBetweenGroups': 'AND',
            'facilityGroupsOperatorBetweenFacilitiesInSameGroup': 'AND',
            'order': 'random',
            'search': '',
            'imagetag': '',
            'occasion[from]': '',
            'occasion[to]': '',
        }

        async with aiohttp.ClientSession() as session:
            for page in range(0, 9):  # Pages 0 to 8
                params['page'] = str(page)  # Update the page parameter
                async with session.get(base_url, params=params, headers=self.headers) as response:
                    if response.status == 200:
                        response_json = await response.json()
                        self.items.extend(response_json.get("items", []))  # Append items from each page
                    else:
                        print(f"Failed to fetch page {page}. Status: {response.status}")

    async def iterate_items(self, session, headers):
        tasks = []
        for item in tqdm(self.items, desc="Processing camping sites"):
            soup = BeautifulSoup(item, 'lxml', parse_only=SoupStrainer('a'))
            link_url = ""
            for link in soup.find_all('a', href=True):
                link_url = 'https://camping.se' + link['href']
                break

            if link_url:
                tasks.append(self.fetch_item_page(session, link_url, headers))

        pages = await asyncio.gather(*tasks)

        for page_soup in pages:
            page_soup = BeautifulSoup(page_soup, 'lxml')

            # Extract the favorite node ID
            favorite_node_id = None
            favorite_button = page_soup.find('button', class_='favorite-button')
            if favorite_button:
                favorite_node_id = favorite_button.get('data-favorite-node-id')

            # Try to extract the name from the <h1> tag
            site_name = None
            h1_tag = page_soup.find('h1', class_='m-0')
            if h1_tag:
                site_name = h1_tag.get_text(strip=True)

            # Fallback to aria-label in the main div if <h1> isn't found
            if not site_name:
                name_div = page_soup.find('div', class_='node')
                site_name = name_div['aria-label'] if name_div and 'aria-label' in name_div.attrs else "Unknown"

            # Extract latitude and longitude
            map_wrapper = page_soup.find('div', id='map-wrapper')
            if map_wrapper:
                data_lat = float(map_wrapper.get('data-lat', ""))
                data_lng = float(map_wrapper.get('data-lng', ""))

                site = Site(
                    drupal_id=favorite_node_id or "Unknown",
                    name=site_name,
                    lat=data_lat,
                    long=data_lng
                )
                self.sites.append(site)

        self.export_to_geojson("camping_sites.geojson")

    async def start(self):
        await self.fetch_list_of_sites()
        print(f"got {len(self.items)} campsites")
        #exit()

        async with aiohttp.ClientSession() as session:
            await self.iterate_items(session, self.headers)

    def export_to_geojson(self, filename: str):
        dictionaries = []
        for site in self.sites:
            site.generate_url()
            dump = site.model_dump(exclude={"lat", "long"})
            dictionaries.append(dump)

        gdf = gpd.GeoDataFrame(dictionaries, geometry=[Point(site.long, site.lat) for site in self.sites],
                               crs="EPSG:4326")

        gdf.to_file(filename, driver='GeoJSON')
        print(f"Exported {len(self.sites)} sites to {filename}")


# Run the async function using asyncio
camping_list = CampingList()
asyncio.run(camping_list.start())
