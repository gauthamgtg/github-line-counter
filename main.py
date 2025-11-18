from flask import Flask, render_template, request, jsonify
import requests
from datetime import datetime
import os

app = Flask(__name__)

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

@app.route('/')
def index():
    return render_template('index.html')

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
    
    if token:
        print(f"[LOG] Using GraphQL API with authentication for user: {username}")
    else:
        print(f"[LOG] Using GraphQL API (unauthenticated) for user: {username}")
        print("[LOG] Note: Using API key increases rate limit from 60 to 5000 requests/hour")
    
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
        print(f"[LOG] Fetching page {page_count} of repositories...")
        
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
            print("[LOG] Using authenticated request with API token")
        
        try:
            response = requests.post(
                GITHUB_GRAPHQL_URL,
                json=payload,
                headers=headers
            )
            
            print(f"[LOG] GraphQL response status: {response.status_code}")
            
            # Handle HTTP status code errors first
            if response.status_code == 401:
                print("[LOG] Error: GitHub API authentication failed (401)")
                return None, "GitHub API authentication failed. Please check your API token if using one.", 401
            elif response.status_code == 403:
                print("[LOG] Error: GitHub API rate limit reached (403)")
                return None, "GitHub API rate limit reached. Please try again later. The limit resets hourly.", 403
            elif response.status_code == 429:
                print("[LOG] Error: GitHub API rate limit exceeded (429)")
                return None, "Too many requests. GitHub API rate limit exceeded. Please wait a few minutes and try again.", 429
            elif response.status_code == 500:
                print("[LOG] Error: GitHub API server error (500)")
                return None, "GitHub API server error. Please try again later.", 500
            elif response.status_code == 503:
                print("[LOG] Error: GitHub API service unavailable (503)")
                return None, "GitHub API service is temporarily unavailable. Please try again later.", 503
            elif response.status_code != 200:
                error_msg = f"GraphQL request failed with status {response.status_code}"
                print(f"[LOG] Error: {error_msg}")
                # Try to get error message from response
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
                print(f"[LOG] Error: Failed to parse JSON response: {str(e)}")
                return None, "Invalid response from GitHub API. Please try again.", 500
            
            # Check for GraphQL errors in response body (GraphQL returns 200 even with errors)
            if 'errors' in data:
                error_messages = [err.get('message', 'Unknown error') for err in data['errors']]
                error_msg = '; '.join(error_messages)
                error_type = data['errors'][0].get('type', '') if data['errors'] else ''
                print(f"[LOG] GraphQL errors: {error_msg} (Type: {error_type})")
                
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
                print(f"[LOG] Rate limit remaining: {remaining}")
                
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
            
            print(f"[LOG] Fetched {len(repos)} repositories in this page")
            all_repos.extend(repos)
            
            has_next_page = page_info.get('hasNextPage', False)
            cursor = page_info.get('endCursor')
            
            if has_next_page:
                print(f"[LOG] More pages available, continuing...")
            
        except requests.exceptions.RequestException as e:
            print(f"[LOG] Network error in GraphQL request: {str(e)}")
            return None, f"Network error: {str(e)}", 500
        except Exception as e:
            print(f"[LOG] Error processing GraphQL response: {str(e)}")
            import traceback
            print(f"[LOG] Traceback: {traceback.format_exc()}")
            return None, f"Error processing response: {str(e)}", 500
    
    print(f"[LOG] Total repositories fetched: {len(all_repos)}")
    return all_repos, None, 200

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        print("[LOG] Analyze request received")
        username = request.json.get('username', '').strip()
        print(f"[LOG] Username extracted: {username}")
        
        if not username:
            print("[LOG] Error: Empty username provided")
            return jsonify({'error': 'Please enter a GitHub username'}), 400
        
        # Get API token from request (optional) or use environment variable
        api_token = request.json.get('api_token', '').strip() or None
        if api_token:
            print("[LOG] API token provided in request")
        elif GITHUB_TOKEN:
            print("[LOG] Using API token from environment variable")
        
        # Fetch repos using GraphQL API
        repos, error_msg, status_code = fetch_repos_with_graphql(username, api_token)
        
        if repos is None:
            # Handle specific error cases - use error_msg from GraphQL function which has detailed messages
            if status_code == 404:
                print(f"[LOG] Error: User '{username}' not found")
                return jsonify({'error': error_msg}), 404
            elif status_code == 401:
                print("[LOG] Error: GitHub API authentication failed (401)")
                return jsonify({'error': error_msg}), 401
            elif status_code == 403:
                print("[LOG] Error: GitHub API rate limit reached (403)")
                return jsonify({'error': error_msg}), 403
            elif status_code == 429:
                print("[LOG] Error: GitHub API rate limit exceeded (429)")
                return jsonify({'error': error_msg}), 429
            elif status_code == 500:
                print("[LOG] Error: GitHub API server error (500)")
                return jsonify({'error': error_msg}), 500
            elif status_code == 503:
                print("[LOG] Error: GitHub API service unavailable (503)")
                return jsonify({'error': error_msg}), 503
            else:
                print(f"[LOG] Error: {error_msg} (Status: {status_code})")
                return jsonify({'error': error_msg if error_msg else 'An unexpected error occurred. Please try again later.'}), status_code if status_code else 500
        
        print(f"[LOG] Found {len(repos)} total repositories")
        total_lines = 0
        repo_data = []
        
        for idx, repo in enumerate(repos):
            repo_name = repo.get('name', 'Unknown')
            print(f"[LOG] Processing repo {idx + 1}/{len(repos)}: {repo_name}")
            
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
                print(f"[LOG] Repository '{repo_name}': {repo_lines:,} lines of code")
                
                repo_data.append({
                    'name': repo_name,
                    'lines': repo_lines,
                    'languages': languages,
                    'stars': repo.get('stargazerCount', 0),
                    'url': repo.get('url', '')
                })
            else:
                print(f"[LOG] Repository '{repo_name}': No code found (empty or binary only)")
        
        print(f"[LOG] Total lines of code: {total_lines:,}")
        print(f"[LOG] Processed {len(repo_data)} original repositories")
        
        # Sort repos by lines
        repo_data.sort(key=lambda x: x['lines'], reverse=True)
        print("[LOG] Repositories sorted by lines of code")
        
        milestone = get_milestone_info(total_lines)
        print(f"[LOG] Milestone determined: {milestone.get('title', 'Unknown')}")
        
        milestone_progress = get_next_milestone(total_lines)
        print(f"[LOG] Progress to next milestone: {milestone_progress['percentage']}%")
        
        language_distribution = get_language_distribution(repo_data)
        print(f"[LOG] Language distribution calculated: {len(language_distribution)} languages")
        
        funny_stats = get_funny_stats(total_lines, len(repo_data))
        print(f"[LOG] Generated {len(funny_stats)} funny stats")
        
        print(f"[LOG] Analysis complete for user '{username}'")
        return jsonify({
            'success': True,
            'username': username,
            'total_lines': total_lines,
            'repo_count': len(repo_data),
            'repos': repo_data,
            'milestone': milestone,
            'milestone_progress': milestone_progress,
            'language_distribution': language_distribution,
            'funny_stats': funny_stats
        })
        
    except requests.exceptions.RequestException as e:
        print(f"[LOG] Network error occurred: {str(e)}")
        return jsonify({'error': f'Network error: Unable to connect to GitHub API. Please check your internet connection and try again.'}), 500
    except ValueError as e:
        print(f"[LOG] JSON parsing error: {str(e)}")
        return jsonify({'error': f'Data parsing error: {str(e)}. Please try again.'}), 500
    except KeyError as e:
        print(f"[LOG] Missing key error: {str(e)}")
        return jsonify({'error': f'Data structure error: Missing expected data field. Please try again.'}), 500
    except Exception as e:
        print(f"[LOG] Unexpected error: {type(e).__name__}: {str(e)}")
        import traceback
        print(f"[LOG] Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'An unexpected error occurred: {str(e)}. Please try again later.'}), 500

if __name__ == '__main__':
    print("✨ GitHub Code Analyzer is starting...")
    print("🌐 Open your browser and go to: http://127.0.0.1:5000")
    print("🚀 Press Ctrl+C to stop the server")
    app.run(debug=True, port=5000)
