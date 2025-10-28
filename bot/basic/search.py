import asyncio
import re
import random
from typing import Union

import httpx

from bot.logger import LOGGER

log = LOGGER(__name__)

ANILIST_URL = ["https://graphql.anilist.co", "https://anillist-zyox.vercel.app/api/graphql", "https://anillist.vercel.app/api/graphql"]
ANILIST_URL = random.choice(ANILIST_URL)
# Headers to avoid 403 Forbidden errors
HEADERS = {
    'User-Agent': 'AnimeBot/1.0 (https://github.com/yourusername/yourbot)',
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

query = """
query ($search: String) {
  Page(page: 1, perPage: 50) {
    media(search: $search, type: ANIME) {
      id
      title {
        english
        romaji
      }
    }
  }
}
"""


async def search(name: str) -> list[list[str, int]]:
    """
    Searches for anime on AniList and returns a list of lists,
    where each inner list contains the anime title and its ID.

    Args:
        name: The search term.

    Returns:
        A list of lists, where each inner list contains the anime title (string) and its ID (integer).
        Returns an empty list if no matches are found.
    """
    variables = {"search": name}
    async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
        # Rate limiting to avoid 403 errors
        await asyncio.sleep(0.5)
        
        try:
            response = await client.post(
                ANILIST_URL, json={"query": query, "variables": variables}
            )
            response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                log.error(f"403 Forbidden - possibly rate limited or blocked IP for search: {name}")
                await asyncio.sleep(2)  # Wait longer before potential retry
                return []
            raise
            
        data = response.json()["data"]["Page"]["media"]
        if not data:
            return []  # Return an empty list if no matches are found.

        results = []
        for anime in data:
            title = anime["title"]["english"] or anime["title"]["romaji"]
            anime_id = anime["id"]
            results.append([title, anime_id])

        return results


anime_query_by_id = """
query ($id: Int) {
  Media(id: $id, type: ANIME) {
    id
    episodes
    status
    title {
      english
      romaji
    }
    nextAiringEpisode {
      episode
    }
  }
}
"""


async def get_anime_info(anime_id: int) -> list[str | int] | None:
    """
    Fetches anime title and total or currently released episodes by anime ID from AniList.

    Args:
        anime_id: The AniList ID of the anime.

    Returns:
        A list containing the anime title (string) and number of available episodes (int),
        or None if not found.
    """
    variables = {"id": anime_id}
    async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
        # Rate limiting to avoid 403 errors
        await asyncio.sleep(0.5)
        
        try:
            response = await client.post(
                ANILIST_URL, json={"query": anime_query_by_id, "variables": variables}
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                log.error(f"403 Forbidden for anime ID {anime_id}")
                return None
            raise
            
        result = response.json()

    media = result.get("data", {}).get("Media")
    if not media:
        return None

    title = media["title"]["english"] or media["title"]["romaji"]
    status = media.get("status")
    total_episodes = media.get("episodes")

    if status == "RELEASING":
        next_ep = media.get("nextAiringEpisode", {}).get("episode")
        released_episodes = next_ep - 1 if next_ep else None
        return [title, released_episodes or total_episodes]
    else:
        return [title, total_episodes]


full_info_query = """
query ($id: Int) {
  Media(id: $id, type: ANIME) {
    id
    title {
      romaji
      english
    }
    description
    format
    status
    episodes
    duration
    startDate {
      year
      month
      day
    }
    endDate {
      year
      month
      day
    }
    averageScore
    genres
    coverImage {
      large
    }
    nextAiringEpisode {
      episode
      airingAt
    }
    relations {
      edges {
        relationType
        node {
          id
        }
      }
    }
  }
}
"""


async def getinfo(anime_id: int, upload: bool = False) -> Union[
    tuple[str, str, int | None, int | None, int | str, str],
    tuple[str, int | None, int | None, int | str, str],
]:
    variables = {"id": anime_id}
    async with httpx.AsyncClient(timeout=10, headers=HEADERS) as client:
        # Rate limiting to avoid 403 errors
        await asyncio.sleep(0.5)
        
        try:
            response = await client.post(
                ANILIST_URL,
                json={"query": full_info_query, "variables": variables},
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                log.error(f"403 Forbidden for getinfo anime ID {anime_id}")
                raise
            raise
            
        media = response.json()["data"]["Media"]

    def get_date(date_obj):
        if not date_obj or not date_obj.get("year"):
            return "N/A"
        return (
            f"{date_obj['year']}-{date_obj['month'] or '??'}-{date_obj['day'] or '??'}"
        )

    # Clean description
    description = re.sub(r"<.*?>", "", media.get("description", "N/A")).strip()
    short_description = (
        (description[:300] + "...") if len(description) > 300 else description
    )

    # Titles and metadata
    title_romaji = media["title"].get("romaji", "N/A")
    title_english = media["title"].get("english", "N/A")
    title = title_english or title_romaji
    format_ = media.get("format", "N/A")
    status = media.get("status", "N/A")
    episodes = media.get("episodes", "N/A")
    avg_score = media.get("averageScore", "N/A")
    genres = ", ".join(media.get("genres", [])) or "N/A"
    cover_url = f"https://img.anili.st/media/{anime_id}"

    # Current released episodes
    next_ep = media.get("nextAiringEpisode")
    if status == "RELEASING" and next_ep:
        current_episode = next_ep["episode"] - 1
    elif status == "FINISHED":
        current_episode = episodes or "Unknown"
    else:
        current_episode = 0

    # Prequel and Sequel detection
    prequel = sequel = None
    for edge in media["relations"]["edges"]:
        relation = edge["relationType"]
        rel_id = edge["node"]["id"]
        if relation == "PREQUEL":
            prequel = rel_id
        elif relation == "SEQUEL":
            sequel = rel_id

    if upload:
        return title, prequel, sequel, current_episode, status

    caption = (
        f"<blockquote><b>{title}</b></blockquote>\n"
        f"<blockquote>‣ Genres: {genres}</blockquote>\n"
        f"<blockquote>‣ Type: {format_} | Rating: {avg_score}</blockquote>\n"
        f"<blockquote>‣ Status: {status} | Episodes: {episodes}</blockquote>\n"
        f"<blockquote>‣ Synopsis: {short_description}</blockquote>"
    )

    return cover_url, caption, prequel, sequel, current_episode, status


async def get_anime_name(anilist_id: int) -> str:
    query = """
    query ($id: Int) {
      Media(id: $id, type: ANIME) {
        title {
          romaji
          english
          native
        }
      }
    }
    """

    variables = {"id": anilist_id}

    async with httpx.AsyncClient(headers=HEADERS) as client:
        # Rate limiting to avoid 403 errors
        await asyncio.sleep(0.5)
        
        try:
            response = await client.post(ANILIST_URL, json={"query": query, "variables": variables})
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 403:
                log.error(f"403 Forbidden for get_anime_name ID {anilist_id}")
                return f"Error: 403 Forbidden (Rate limited or blocked)"
            raise
            
        data = response.json()

        # Handle possible errors
        if "errors" in data:
            return f"Error: {data['errors'][0]['message']}"

        title = data["data"]["Media"]["title"]
        return title.get("english") or title.get("romaji") or title.get("native")
