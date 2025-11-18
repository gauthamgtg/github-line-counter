import flet as ft
import requests
import os
import threading

# GitHub GraphQL API endpoint
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

# Get GitHub API key from environment variable
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', None)

def get_milestone_info(lines):
    milestones = [
        (0, "🐣 Hatchling Coder", "You're just getting started!", "#4a9eff", 
         "Fun Fact: That's like writing a shopping list!", "hatchling"),
        (100, "🌱 Code Sprout", "Nice! You've planted the seed!", "#5cb85c",
         "Fun Fact: That's about 1 SMS message worth of code!", "sprout"),
        (500, "🔥 Keyboard Warrior", "You're on fire!", "#ff6b6b",
         "Fun Fact: You've written more code than lines in a children's book!", "warrior"),
        (1000, "⚡ Code Ninja", "Sneaky fast coding!", "#f39c12",
         "Fun Fact: That's enough to crash a small website!", "ninja"),
        (5000, "🎯 Bug Creator Pro", "With great code comes great bugs!", "#9b59b6",
         "Fun Fact: Statistically, you've introduced 50 bugs by now!", "bug"),
        (10000, "🏆 Code Veteran", "Impressive! You've seen some things...", "#e74c3c",
         "Fun Fact: That's about 200 pages of a novel!", "veteran"),
        (25000, "💎 Diamond Developer", "You're precious!", "#3498db",
         "Fun Fact: You've typed more than Shakespeare's Hamlet!", "diamond"),
        (50000, "🌟 Code Wizard", "Magic happens at your fingertips!", "#f1c40f",
         "Fun Fact: You could print this and use it as a weapon!", "wizard"),
        (100000, "🚀 Code Astronaut", "You're in orbit now!", "#16a085",
         "Fun Fact: This is like writing 4 full textbooks!", "astronaut"),
        (250000, "👑 Code Monarch", "You rule the codebase!", "#8e44ad",
         "Fun Fact: That's enough code to confuse any code reviewer!", "monarch"),
        (500000, "🦸 Code Superhero", "Not all heroes wear capes!", "#c0392b",
         "Fun Fact: You've written more lines than the original Linux kernel!", "superhero"),
        (1000000, "🌌 Code Legend", "LEGENDARY STATUS ACHIEVED!", "#d35400",
         "Fun Fact: You've basically written the next operating system!", "legend"),
    ]
    
    for i in range(len(milestones) - 1, -1, -1):
        if lines >= milestones[i][0]:
            return {
                'title': milestones[i][1],
                'subtitle': milestones[i][2],
                'color': milestones[i][3],
                'fact': milestones[i][4],
                'class': milestones[i][5]
            }
    return {
        'title': milestones[0][1],
        'subtitle': milestones[0][2],
        'color': milestones[0][3],
        'fact': milestones[0][4],
        'class': milestones[0][5]
    }

def get_next_milestone(lines):
    """Calculate progress to next milestone"""
    milestones = [0, 100, 500, 1000, 5000, 10000, 25000, 50000, 100000, 250000, 500000, 1000000]
    current_milestone = 0
    next_milestone = 100
    
    if lines >= milestones[-1]:
        current_milestone = milestones[-1]
        next_milestone = milestones[-1] * 2  # Double the last milestone
    else:
        for i in range(len(milestones) - 1):
            if milestones[i] <= lines < milestones[i + 1]:
                current_milestone = milestones[i]
                next_milestone = milestones[i + 1]
                break
    
    progress = ((lines - current_milestone) / (next_milestone - current_milestone)) * 100 if next_milestone > current_milestone else 100
    remaining = next_milestone - lines
    
    return {
        'current': current_milestone,
        'next': next_milestone,
        'progress': min(100, max(0, progress)),
        'remaining': max(0, remaining),
        'percentage': round(progress, 1)
    }

def get_language_distribution(repos):
    """Calculate language distribution across all repos"""
    lang_total = {}
    total_lines = 0
    
    for repo in repos:
        for lang, size in repo.get('languages', {}).items():
            lang_total[lang] = lang_total.get(lang, 0) + size
            total_lines += size
    
    # Calculate percentages and sort
    lang_dist = []
    for lang, size in sorted(lang_total.items(), key=lambda x: x[1], reverse=True):
        percentage = (size / total_lines * 100) if total_lines > 0 else 0
        lang_dist.append({
            'name': lang,
            'lines': size,
            'percentage': round(percentage, 2)
        })
    
    return lang_dist

def get_funny_stats(lines, repos):
    stats = []
    coffee = lines // 1000
    stats.append({'icon': '☕', 'label': 'Coffee cups needed', 'value': f'{coffee:,}'})
    
    keyboards = lines // 5000
    stats.append({'icon': '⌨️', 'label': 'Keyboards destroyed', 'value': f'{keyboards:,}'})
    
    so_visits = lines // 500
    stats.append({'icon': '🔍', 'label': 'Stack Overflow visits', 'value': f'{so_visits:,}+'})
    
    bugs = lines // 150
    stats.append({'icon': '🐛', 'label': 'Bugs created', 'value': f'~{bugs:,}'})
    
    hours = lines // 300
    stats.append({'icon': '⏰', 'label': 'Hours of coding', 'value': f'~{hours:,}h'})
    
    # More creative stats
    commits = lines // 150
    stats.append({'icon': '💾', 'label': 'Estimated commits', 'value': f'~{commits:,}'})
    
    if lines > 0:
        avg_repo = lines // max(repos, 1)
        stats.append({'icon': '📦', 'label': 'Avg lines per repo', 'value': f'{avg_repo:,}'})
    
    if lines > 50000:
        stats.append({'icon': '🌌', 'label': 'Code density', 'value': 'Matrix Level'})
    elif lines > 10000:
        stats.append({'icon': '⚡', 'label': 'Code density', 'value': 'High'})
    else:
        stats.append({'icon': '💫', 'label': 'Code density', 'value': 'Growing'})
    
    if lines > 100000:
        stats.append({'icon': '📚', 'label': 'Equivalent to', 'value': f'{lines // 25000} novels'})
    elif lines > 10000:
        stats.append({'icon': '📖', 'label': 'Equivalent to', 'value': f'{lines // 2500} short stories'})
    else:
        stats.append({'icon': '📝', 'label': 'Equivalent to', 'value': f'{lines // 50} blog posts'})
    
    # Code complexity metrics
    if lines > 1000000:
        stats.append({'icon': '👑', 'label': 'Status', 'value': 'Code Deity'})
    elif lines > 500000:
        stats.append({'icon': '🚀', 'label': 'Status', 'value': 'Code Legend'})
    elif lines > 100000:
        stats.append({'icon': '⭐', 'label': 'Status', 'value': 'Code Master'})
    elif lines > 50000:
        stats.append({'icon': '🔥', 'label': 'Status', 'value': 'Code Warrior'})
    else:
        stats.append({'icon': '🌱', 'label': 'Status', 'value': 'Code Sprout'})
    
    # Add typing speed estimate
    wpm = 60  # average typing speed
    chars_per_line = 50  # average
    typing_hours = (lines * chars_per_line) / (wpm * 5 * 60)  # 5 chars per word
    stats.append({'icon': '⌨️', 'label': 'Typing time (est)', 'value': f'{int(typing_hours):,}h'})
    
    return stats

def fetch_repos_with_graphql(username, api_token=None):
    """
    Fetch user repositories and their languages using GitHub GraphQL API.
    This is much more efficient than REST API as it requires only 1-2 requests.
    
    Args:
        username: GitHub username to analyze
        api_token: Optional GitHub API token for authenticated requests (increases rate limit)
    """
    # Use provided token or fall back to environment variable
    token = api_token or GITHUB_TOKEN
    
    # GraphQL query to fetch repos with languages
    query_template = """
    query($username: String!, $cursor: String) {
      user(login: $username) {
        repositories(
          first: 100
          after: $cursor
          ownerAffiliations: OWNER
          isFork: false
          orderBy: {field: UPDATED_AT, direction: DESC}
        ) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            name
            url
            stargazerCount
            languages(first: 20) {
              edges {
                size
                node {
                  name
                }
              }
            }
          }
        }
      }
      rateLimit {
        remaining
        resetAt
      }
    }
    """
    
    all_repos = []
    cursor = None
    has_next_page = True
    page_count = 0
    
    while has_next_page:
        page_count += 1
        
        variables = {
            "username": username,
            "cursor": cursor
        }
        
        payload = {
            "query": query_template,
            "variables": variables
        }
        
        # Prepare headers with authentication if token is available
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        try:
            response = requests.post(
                GITHUB_GRAPHQL_URL,
                json=payload,
                headers=headers
            )
            
            # Handle HTTP status code errors first
            if response.status_code == 401:
                return None, "GitHub API authentication failed. Please check your API token if using one.", 401
            elif response.status_code == 403:
                return None, "GitHub API rate limit reached. Please try again later. The limit resets hourly.", 403
            elif response.status_code == 429:
                return None, "Too many requests. GitHub API rate limit exceeded. Please wait a few minutes and try again.", 429
            elif response.status_code == 500:
                return None, "GitHub API server error. Please try again later.", 500
            elif response.status_code == 503:
                return None, "GitHub API service is temporarily unavailable. Please try again later.", 503
            elif response.status_code != 200:
                error_msg = f"GraphQL request failed with status {response.status_code}"
                try:
                    error_data = response.json()
                    if 'message' in error_data:
                        error_msg = error_data['message']
                except:
                    pass
                return None, f"GitHub API error ({response.status_code}): {error_msg}", response.status_code
            
            # Parse JSON response
            try:
                data = response.json()
            except ValueError as e:
                return None, "Invalid response from GitHub API. Please try again.", 500
            
            # Check for GraphQL errors in response body (GraphQL returns 200 even with errors)
            if 'errors' in data:
                error_messages = [err.get('message', 'Unknown error') for err in data['errors']]
                error_msg = '; '.join(error_messages)
                error_type = data['errors'][0].get('type', '') if data['errors'] else ''
                
                # Check if user not found
                if any('Could not resolve to a User' in msg or 'NOT_FOUND' in msg or 'User' in error_type for msg in error_messages):
                    return None, "User not found! Please check the username and try again.", 404
                
                # Check for rate limit in GraphQL errors
                if any('rate limit' in msg.lower() or 'RATE_LIMITED' in error_type for msg in error_messages):
                    return None, "GitHub API rate limit reached. Please try again later. The limit resets hourly.", 403
                
                return None, f"GitHub API error: {error_msg}", 500
            
            # Check rate limit from rateLimit field
            if 'data' in data and 'rateLimit' in data['data']:
                rate_limit = data['data']['rateLimit']
                remaining = rate_limit.get('remaining', 0)
                
                if remaining == 0:
                    reset_at = rate_limit.get('resetAt', 'unknown')
                    return None, f"GitHub API rate limit reached. Please try again later. Resets at: {reset_at}", 403
            
            # Extract repositories
            if 'data' not in data or 'user' not in data['data']:
                return None, "Invalid response structure from GitHub API", 500
            
            user_data = data['data']['user']
            
            if user_data is None:
                return None, "User not found! Please check the username and try again.", 404
            
            repos_data = user_data.get('repositories', {})
            repos = repos_data.get('nodes', [])
            page_info = repos_data.get('pageInfo', {})
            
            all_repos.extend(repos)
            
            has_next_page = page_info.get('hasNextPage', False)
            cursor = page_info.get('endCursor')
            
        except requests.exceptions.RequestException as e:
            return None, f"Network error: {str(e)}", 500
        except Exception as e:
            return None, f"Error processing response: {str(e)}", 500
    
    return all_repos, None, 200

def analyze_github_user(username, api_token=None):
    """Analyze GitHub user and return results"""
    if not username:
        return None, "Please enter a GitHub username"
    
    # Fetch repos using GraphQL API
    repos, error_msg, status_code = fetch_repos_with_graphql(username, api_token)
    
    if repos is None:
        return None, error_msg
    
    total_lines = 0
    repo_data = []
    
    for repo in repos:
        repo_name = repo.get('name', 'Unknown')
        
        # Extract languages from GraphQL response
        languages_edges = repo.get('languages', {}).get('edges', [])
        languages = {}
        repo_lines = 0
        
        for lang_edge in languages_edges:
            lang_name = lang_edge.get('node', {}).get('name', '')
            lang_size = lang_edge.get('size', 0)
            if lang_name:
                languages[lang_name] = lang_size
                repo_lines += lang_size
        
        if repo_lines > 0:
            total_lines += repo_lines
            
            repo_data.append({
                'name': repo_name,
                'lines': repo_lines,
                'languages': languages,
                'stars': repo.get('stargazerCount', 0),
                'url': repo.get('url', '')
            })
    
    # Sort repos by lines
    repo_data.sort(key=lambda x: x['lines'], reverse=True)
    
    milestone = get_milestone_info(total_lines)
    milestone_progress = get_next_milestone(total_lines)
    language_distribution = get_language_distribution(repo_data)
    funny_stats = get_funny_stats(total_lines, len(repo_data))
    
    return {
        'success': True,
        'username': username,
        'total_lines': total_lines,
        'repo_count': len(repo_data),
        'repos': repo_data,
        'milestone': milestone,
        'milestone_progress': milestone_progress,
        'language_distribution': language_distribution,
        'funny_stats': funny_stats
    }, None

def main(page: ft.Page):
    page.title = "🚀 GitHub Code Analyzer"
    page.theme_mode = ft.ThemeMode.DARK
    page.bgcolor = "#0a0a0a"
    page.padding = 20
    
    # Header
    header = ft.Container(
        content=ft.Column([
            ft.Text(
                "<GITHUB_CODE_ANALYZER>",
                size=48,
                weight=ft.FontWeight.BOLD,
                text_align=ft.TextAlign.CENTER,
                color="#00ff41"
            ),
            ft.Text(
                "Decode Your Digital DNA...",
                size=18,
                text_align=ft.TextAlign.CENTER,
                color="#aaa"
            )
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=40,
        border=ft.border.all(2, "#00ff41"),
        border_radius=20,
        bgcolor="#1a1a1a",
        margin=ft.margin.only(bottom=40)
    )
    
    # Search section
    username_input = ft.TextField(
        label="GitHub Username",
        hint_text="Enter GitHub username...",
        width=400,
        autofocus=True,
        border_color="#00ff41",
        color="#00ff00"
    )
    
    analyze_button = ft.ElevatedButton(
        "⚡ ANALYZE ⚡",
        on_click=lambda _: start_analysis(),
        bgcolor="#ff006e",
        color="white",
        width=200
    )
    
    search_section = ft.Container(
        content=ft.Row([
            username_input,
            analyze_button
        ], alignment=ft.MainAxisAlignment.CENTER),
        padding=40,
        border=ft.border.all(2, "#00ff41"),
        border_radius=15,
        bgcolor="#1a1a1a",
        margin=ft.margin.only(bottom=40)
    )
    
    # Loading indicator
    loading_indicator = ft.Container(
        content=ft.Column([
            ft.ProgressRing(),
            ft.Text("SCANNING THE DIGITAL ABYSS...", size=16, color="#ff006e")
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=20),
        padding=40,
        visible=False
    )
    
    # Error message
    error_text = ft.Text(
        "",
        color="#ff0000",
        size=16,
        text_align=ft.TextAlign.CENTER,
        visible=False
    )
    
    # Results container
    results_container = ft.Container(visible=False)
    
    def start_analysis():
        username = username_input.value.strip()
        if not username:
            show_error("Please enter a GitHub username")
            return
        
        # Hide results, show loading
        results_container.visible = False
        error_text.visible = False
        loading_indicator.visible = True
        analyze_button.disabled = True
        page.update()
        
        def analyze_thread():
            result, error = analyze_github_user(username)
            page.run_thread(lambda: display_results(result, error))
        
        threading.Thread(target=analyze_thread, daemon=True).start()
    
    def display_results(result, error):
        loading_indicator.visible = False
        analyze_button.disabled = False
        
        if error:
            show_error(error)
            return
        
        if not result:
            show_error("An unexpected error occurred")
            return
        
        # Build results UI
        results_content = []
        
        # Total lines
        total_lines_text = ft.Text(
            f"{result['total_lines']:,}",
            size=72,
            weight=ft.FontWeight.BOLD,
            color="#00ff41",
            text_align=ft.TextAlign.CENTER
        )
        results_content.append(
            ft.Container(
                content=ft.Column([
                    total_lines_text,
                    ft.Text("LINES OF CODE", size=20, color="#aaa", text_align=ft.TextAlign.CENTER)
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                padding=40,
                border=ft.border.all(2, "#00ff41"),
                border_radius=20,
                bgcolor="#1a1a1a",
                margin=ft.margin.only(bottom=20)
            )
        )
        
        # Milestone
        milestone = result['milestone']
        milestone_badge = ft.Container(
            content=ft.Column([
                ft.Text(milestone['title'], size=32, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                ft.Text(milestone['subtitle'], size=18, text_align=ft.TextAlign.CENTER, color="#ccc"),
                ft.Text(milestone['fact'], size=14, text_align=ft.TextAlign.CENTER, color="#ff006e", italic=True)
            ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
            padding=30,
            border=ft.border.all(3, milestone['color']),
            border_radius=15,
            bgcolor=milestone['color'],
            margin=ft.margin.only(bottom=20)
        )
        results_content.append(milestone_badge)
        
        # Progress bar
        progress = result['milestone_progress']
        progress_bar = ft.Container(
            content=ft.Column([
                ft.Row([
                    ft.Text("Progress to Next Milestone", size=14),
                    ft.Text(f"{progress['percentage']}%", size=14, weight=ft.FontWeight.BOLD)
                ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                ft.ProgressBar(value=progress['percentage'] / 100, color="#00ff41", bgcolor="#1a1a1a"),
                ft.Text(
                    f"{progress['remaining']:,} lines until next milestone ({progress['next']:,} lines)",
                    size=12,
                    color="#aaa"
                )
            ], spacing=10),
            padding=20,
            border=ft.border.all(2, "#00ff41"),
            border_radius=15,
            bgcolor="#0a0a0a",
            margin=ft.margin.only(bottom=20)
        )
        results_content.append(progress_bar)
        
        # Language distribution
        if result['language_distribution']:
            lang_items = []
            for lang in result['language_distribution'][:10]:  # Top 10
                lang_items.append(
                    ft.Container(
                        content=ft.Row([
                            ft.Text(lang['name'], size=14, weight=ft.FontWeight.BOLD, width=150, color="#00ff41"),
                            ft.ProgressBar(value=lang['percentage'] / 100, width=200, color="#00ff41", bgcolor="#1a1a1a"),
                            ft.Text(f"{lang['percentage']}%", size=12, width=80, text_align=ft.TextAlign.RIGHT)
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        padding=10,
                        border=ft.border.all(1, "#00ff41"),
                        border_radius=10,
                        bgcolor="#0a0a0a",
                        margin=ft.margin.only(bottom=10)
                    )
                )
            
            results_content.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text("Language Distribution", size=24, weight=ft.FontWeight.BOLD, color="#00ff41"),
                        ft.Column(lang_items, spacing=5)
                    ], spacing=15),
                    padding=30,
                    border=ft.border.all(2, "#00ff41"),
                    border_radius=20,
                    bgcolor="#1a1a1a",
                    margin=ft.margin.only(bottom=20)
                )
            )
        
        # Funny stats
        stats_grid = []
        for stat in result['funny_stats']:
            stats_grid.append(
                ft.Container(
                    content=ft.Column([
                        ft.Text(stat['icon'], size=48),
                        ft.Text(stat['value'], size=20, weight=ft.FontWeight.BOLD, color="#00ff41"),
                        ft.Text(stat['label'], size=12, color="#aaa")
                    ], horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
                    padding=20,
                    border=ft.border.all(2, "#00ff41"),
                    border_radius=15,
                    bgcolor="#1a1a1a",
                    width=200,
                    height=200
                )
            )
        
        results_content.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("Fun Stats", size=24, weight=ft.FontWeight.BOLD, color="#00ff41"),
                    ft.Row(stats_grid, wrap=True, spacing=10)
                ], spacing=15),
                padding=30,
                margin=ft.margin.only(bottom=20)
            )
        )
        
        # Repositories
        repo_cards = []
        for repo in result['repos'][:20]:  # Top 20 repos
            lang_tags = []
            for lang, size in sorted(repo['languages'].items(), key=lambda x: x[1], reverse=True)[:5]:
                lang_tags.append(
                    ft.Chip(
                        label=ft.Text(f"{lang} ({size:,})", size=10),
                        bgcolor="#0a0a0a",
                        border=ft.border.all(1, "#00ff41")
                    )
                )
            
            repo_cards.append(
                ft.Container(
                    content=ft.Column([
                        ft.Row([
                            ft.Text(repo['name'], size=18, weight=ft.FontWeight.BOLD, color="#00ff41", expand=True),
                            ft.Text(f"{repo['lines']:,} lines", size=16, color="#00ff41", weight=ft.FontWeight.BOLD),
                            ft.Text(f"⭐ {repo['stars']}", size=14, color="#f1c40f") if repo['stars'] > 0 else ft.Container()
                        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Wrap(lang_tags, spacing=5) if lang_tags else ft.Container()
                    ], spacing=10),
                    padding=20,
                    border=ft.border.all(2, "#00ff41"),
                    border_radius=15,
                    bgcolor="#1a1a1a",
                    margin=ft.margin.only(bottom=15)
                )
            )
        
        results_content.append(
            ft.Container(
                content=ft.Column([
                    ft.Text("Repository Breakdown", size=24, weight=ft.FontWeight.BOLD, color="#00ff41"),
                    ft.Column(repo_cards, spacing=10)
                ], spacing=15),
                padding=30,
                border=ft.border.all(2, "#00ff41"),
                border_radius=20,
                bgcolor="#1a1a1a"
            )
        )
        
        results_container.content = ft.Column(results_content, spacing=20, scroll=ft.ScrollMode.AUTO)
        results_container.visible = True
        error_text.visible = False
        page.update()
    
    def show_error(message):
        error_text.value = message
        error_text.visible = True
        results_container.visible = False
        page.update()
    
    # Handle Enter key
    def on_keyboard(e: ft.KeyboardEvent):
        if e.key == "Enter":
            start_analysis()
    
    page.on_keyboard_event = on_keyboard
    
    # Add Enter key handler to text field
    username_input.on_submit = lambda _: start_analysis()
    
    # Build page
    page.add(
        header,
        search_section,
        loading_indicator,
        error_text,
        results_container
    )

if __name__ == "__main__":
    ft.app(target=main)

