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
    # Create templates folder and index.html
    import os
    os.makedirs('templates', exist_ok=True)
    
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🚀 GitHub Code Analyzer - Enhanced</title>
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400;700&family=Orbitron:wght@400;700;900&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        :root {
            --color-bg: #0a0a0a;
            --color-text: #00ff00;
            --color-primary: #00ff41;
            --color-secondary: #ff006e;
            --color-accent: #8338ec;
            --color-card-bg: #1a1a1a;
            --font-mono: 'Roboto Mono', monospace;
            --font-futuristic: 'Orbitron', monospace;
        }
        
        body {
            font-family: var(--font-mono);
            background: linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 100%);
            min-height: 100vh;
            color: var(--color-text);
            overflow-x: hidden;
            position: relative;
        }
        
        /* Enhanced Matrix Rain Effect */
        #matrix-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            pointer-events: none;
            overflow: hidden;
            opacity: 0.3;
        }
        
        .matrix-column {
            position: absolute;
            top: -100%;
            color: var(--color-primary);
            font-size: 16px;
            font-family: var(--font-mono);
            text-shadow: 0 0 10px rgba(0, 255, 65, 0.8);
            animation: matrix-fall linear infinite;
        }
        
        @keyframes matrix-fall {
            0% {
                transform: translateY(-100%);
                opacity: 0;
            }
            10% {
                opacity: 1;
            }
            90% {
                opacity: 1;
            }
            100% {
                transform: translateY(calc(100vh + 100%));
                opacity: 0;
            }
        }
        
        /* Confetti Canvas */
        #confetti-canvas {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9999;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            z-index: 1;
        }
        
        .header {
            text-align: center;
            padding: 80px 20px;
            background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(26, 26, 46, 0.9) 100%);
            border-radius: 20px;
            margin-bottom: 40px;
            box-shadow: 
                0 0 50px rgba(0, 255, 65, 0.2),
                inset 0 0 50px rgba(0, 255, 65, 0.05);
            border: 2px solid var(--color-primary);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }
        
        .header::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(0, 255, 65, 0.15) 0%, transparent 70%);
            animation: pulse 4s ease-in-out infinite;
        }
        
        .header::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(0, 255, 65, 0.1), transparent);
            animation: scan 3s linear infinite;
        }
        
        @keyframes pulse {
            0%, 100% { 
                transform: scale(1); 
                opacity: 0.5;
            }
            50% { 
                transform: scale(1.2); 
                opacity: 1;
            }
        }
        
        @keyframes scan {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .header h1 {
            font-size: 4em;
            font-family: var(--font-futuristic);
            color: white;
            margin-bottom: 15px;
            position: relative;
            z-index: 1;
            letter-spacing: 8px;
            text-shadow: 
                0 0 20px var(--color-primary),
                0 0 40px var(--color-primary),
                0 0 60px rgba(0, 255, 65, 0.5);
            animation: glow 2s ease-in-out infinite alternate;
        }
        
        @keyframes glow {
            from {
                text-shadow: 
                    0 0 20px var(--color-primary),
                    0 0 40px var(--color-primary),
                    0 0 60px rgba(0, 255, 65, 0.5);
            }
            to {
                text-shadow: 
                    0 0 30px var(--color-primary),
                    0 0 60px var(--color-primary),
                    0 0 90px rgba(0, 255, 65, 0.8);
            }
        }
        
        .header p {
            font-size: 1.4em;
            color: #aaa;
            position: relative;
            z-index: 1;
            text-transform: uppercase;
            letter-spacing: 3px;
        }
        
        .search-section {
            background: rgba(26, 26, 26, 0.8);
            padding: 50px;
            border-radius: 15px;
            margin-bottom: 40px;
            box-shadow: 0 0 40px rgba(0, 255, 65, 0.15);
            border: 2px solid var(--color-primary);
            backdrop-filter: blur(10px);
        }
        
        .input-group {
            display: flex;
            gap: 20px;
            max-width: 700px;
            margin: 0 auto;
        }
        
        input {
            flex: 1;
            padding: 20px 30px;
            font-size: 1.1em;
            font-family: var(--font-mono);
            background: rgba(10, 10, 10, 0.8);
            border: 2px solid var(--color-primary);
            border-radius: 10px;
            color: var(--color-text);
            transition: all 0.3s ease;
        }
        
        input:focus {
            outline: none;
            border-color: var(--color-secondary);
            box-shadow: 
                0 0 20px rgba(255, 0, 110, 0.5),
                inset 0 0 20px rgba(255, 0, 110, 0.1);
            transform: scale(1.02);
        }
        
        button {
            padding: 20px 50px;
            font-size: 1.1em;
            font-weight: bold;
            font-family: var(--font-futuristic);
            text-transform: uppercase;
            background: linear-gradient(135deg, var(--color-secondary) 0%, var(--color-accent) 100%);
            color: white;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 0 20px rgba(255, 0, 110, 0.5);
            letter-spacing: 2px;
        }
        
        button:hover {
            transform: translateY(-3px) scale(1.05);
            box-shadow: 0 0 30px rgba(255, 0, 110, 0.8);
        }
        
        button:active {
            transform: translateY(-1px) scale(1.02);
        }
        
        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .loading {
            text-align: center;
            padding: 80px;
            display: none;
            color: var(--color-secondary);
        }
        
        .loading-content {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 30px;
        }
        
        .spinner-container {
            position: relative;
            width: 100px;
            height: 100px;
        }
        
        .spinner {
            position: absolute;
            width: 100px;
            height: 100px;
            border: 4px solid rgba(0, 255, 65, 0.1);
            border-top: 4px solid var(--color-primary);
            border-right: 4px solid var(--color-secondary);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        
        .spinner-inner {
            position: absolute;
            top: 20px;
            left: 20px;
            width: 60px;
            height: 60px;
            border: 4px solid rgba(0, 255, 65, 0.1);
            border-top: 4px solid var(--color-accent);
            border-radius: 50%;
            animation: spin 0.7s linear infinite reverse;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-text {
            font-size: 1.3em;
            text-transform: uppercase;
            letter-spacing: 3px;
            animation: pulse-text 1.5s ease-in-out infinite;
        }
        
        @keyframes pulse-text {
            0%, 100% { opacity: 0.5; }
            50% { opacity: 1; }
        }
        
        .results {
            display: none;
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .stats-overview {
            background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(26, 26, 46, 0.9) 100%);
            padding: 60px;
            border-radius: 20px;
            text-align: center;
            margin-bottom: 40px;
            box-shadow: 
                0 0 50px rgba(0, 255, 65, 0.2),
                inset 0 0 50px rgba(0, 255, 65, 0.05);
            border: 2px solid var(--color-primary);
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }
        
        .big-number {
            font-size: 6em;
            font-family: var(--font-futuristic);
            font-weight: 900;
            margin-bottom: 15px;
            color: var(--color-primary);
            text-shadow: 
                0 0 20px rgba(0, 255, 65, 0.8),
                0 0 40px rgba(0, 255, 65, 0.6),
                0 0 60px rgba(0, 255, 65, 0.4);
            background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-secondary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .big-number::after {
            content: " LoC";
            font-size: 0.25em;
            vertical-align: super;
            -webkit-text-fill-color: var(--color-text);
        }
        
        .milestone-section {
            margin: 40px 0;
        }
        
        .milestone-badge {
            display: inline-block;
            padding: 25px 60px;
            border-radius: 15px;
            font-size: 2.5em;
            font-family: var(--font-futuristic);
            font-weight: bold;
            margin: 30px 0;
            animation: badgeAppear 0.8s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            box-shadow: 
                0 10px 30px rgba(0, 0, 0, 0.5),
                0 0 30px currentColor;
            border: 3px solid;
            text-transform: uppercase;
            letter-spacing: 3px;
            position: relative;
            overflow: hidden;
        }
        
        .milestone-badge::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            animation: shine 3s infinite;
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%) translateY(-100%) rotate(45deg); }
            100% { transform: translateX(100%) translateY(100%) rotate(45deg); }
        }
        
        @keyframes badgeAppear {
            0% { 
                transform: scale(0) rotate(-180deg);
                opacity: 0;
            }
            60% {
                transform: scale(1.2) rotate(10deg);
            }
            100% { 
                transform: scale(1) rotate(0deg);
                opacity: 1;
            }
        }
        
        .milestone-subtitle {
            font-size: 1.5em;
            color: #ccc;
            margin: 15px 0;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .milestone-fact {
            font-size: 1.2em;
            color: var(--color-secondary);
            font-style: italic;
            padding: 20px;
            border-left: 5px solid var(--color-secondary);
            margin-top: 25px;
            background: rgba(255, 0, 110, 0.1);
            border-radius: 5px;
        }
        
        /* Progress Bar */
        .progress-section {
            margin: 40px 0;
            padding: 30px;
            background: rgba(10, 10, 10, 0.5);
            border-radius: 15px;
            border: 2px solid var(--color-primary);
        }
        
        .progress-label {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            font-size: 1.1em;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .progress-bar-container {
            width: 100%;
            height: 30px;
            background: rgba(0, 255, 65, 0.1);
            border-radius: 15px;
            overflow: hidden;
            border: 2px solid var(--color-primary);
            position: relative;
        }
        
        .progress-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--color-primary) 0%, var(--color-secondary) 100%);
            border-radius: 15px;
            transition: width 1s ease-out;
            box-shadow: 
                0 0 20px rgba(0, 255, 65, 0.6),
                inset 0 0 20px rgba(255, 255, 255, 0.2);
            position: relative;
            overflow: hidden;
        }
        
        .progress-bar::after {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
            animation: progress-shine 2s infinite;
        }
        
        @keyframes progress-shine {
            0% { left: -100%; }
            100% { left: 100%; }
        }
        
        .progress-text {
            margin-top: 10px;
            font-size: 0.9em;
            color: #aaa;
        }
        
        /* Language Distribution */
        .language-section {
            background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(26, 26, 46, 0.9) 100%);
            padding: 40px;
            border-radius: 20px;
            margin-bottom: 40px;
            box-shadow: 0 0 40px rgba(0, 255, 65, 0.15);
            border: 2px solid var(--color-primary);
            backdrop-filter: blur(10px);
        }
        
        .language-chart {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin-top: 30px;
        }
        
        .language-item {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 15px;
            background: rgba(10, 10, 10, 0.5);
            border-radius: 10px;
            border: 1px solid rgba(0, 255, 65, 0.3);
            transition: all 0.3s ease;
        }
        
        .language-item:hover {
            transform: translateX(10px);
            border-color: var(--color-primary);
            box-shadow: 0 0 20px rgba(0, 255, 65, 0.3);
        }
        
        .language-name {
            min-width: 150px;
            font-weight: bold;
            color: var(--color-primary);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .language-bar-container {
            flex: 1;
            height: 25px;
            background: rgba(0, 255, 65, 0.1);
            border-radius: 12px;
            overflow: hidden;
            border: 1px solid rgba(0, 255, 65, 0.3);
            position: relative;
        }
        
        .language-bar {
            height: 100%;
            background: linear-gradient(90deg, var(--color-primary) 0%, var(--color-accent) 100%);
            border-radius: 12px;
            transition: width 1s ease-out;
            box-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
        }
        
        .language-percentage {
            min-width: 80px;
            text-align: right;
            font-weight: bold;
            color: var(--color-text);
        }
        
        .funny-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 40px 0;
        }
        
        .stat-card {
            background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(10, 10, 10, 0.9) 100%);
            padding: 35px;
            border-radius: 15px;
            text-align: center;
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            border: 2px solid var(--color-primary);
            position: relative;
            overflow: hidden;
            backdrop-filter: blur(10px);
        }
        
        .stat-card::before {
            content: '';
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(0, 255, 65, 0.1) 0%, transparent 70%);
            opacity: 0;
            transition: opacity 0.3s ease;
        }
        
        .stat-card:hover {
            transform: translateY(-10px) scale(1.05);
            box-shadow: 
                0 15px 40px rgba(0, 255, 65, 0.4),
                0 0 30px rgba(0, 255, 65, 0.2);
            border-color: var(--color-secondary);
        }
        
        .stat-card:hover::before {
            opacity: 1;
        }
        
        .stat-icon {
            font-size: 4em;
            margin-bottom: 20px;
            display: block;
            animation: float 3s ease-in-out infinite;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-10px); }
        }
        
        .stat-value {
            font-size: 2.2em;
            font-family: var(--font-futuristic);
            font-weight: bold;
            color: var(--color-primary);
            margin: 15px 0;
            text-shadow: 0 0 15px rgba(0, 255, 65, 0.6);
        }
        
        .stat-label {
            color: #aaa;
            font-size: 1em;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .repos-section {
            margin-top: 50px;
            border-top: 3px dashed rgba(0, 255, 65, 0.3);
            padding-top: 40px;
        }
        
        .repos-controls {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .search-box, .sort-select {
            padding: 12px 20px;
            font-family: var(--font-mono);
            background: rgba(10, 10, 10, 0.8);
            border: 2px solid var(--color-primary);
            border-radius: 8px;
            color: var(--color-text);
            font-size: 1em;
        }
        
        .search-box {
            flex: 1;
            min-width: 200px;
        }
        
        .sort-select {
            min-width: 150px;
        }
        
        .section-title {
            font-size: 2.5em;
            font-family: var(--font-futuristic);
            margin-bottom: 30px;
            color: var(--color-primary);
            text-align: center;
            text-shadow: 0 0 20px rgba(0, 255, 65, 0.6);
            text-transform: uppercase;
            letter-spacing: 5px;
        }
        
        .repo-card {
            background: linear-gradient(135deg, rgba(26, 26, 26, 0.9) 0%, rgba(10, 10, 10, 0.9) 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 25px;
            border: 2px solid var(--color-primary);
            transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
            backdrop-filter: blur(10px);
            position: relative;
            overflow: hidden;
        }
        
        .repo-card::before {
            content: '';
            position: absolute;
            left: 0;
            top: 0;
            width: 5px;
            height: 100%;
            background: linear-gradient(180deg, var(--color-primary) 0%, var(--color-secondary) 100%);
            transform: scaleY(0);
            transition: transform 0.3s ease;
        }
        
        .repo-card:hover {
            transform: translateX(15px) scale(1.02);
            box-shadow: 
                0 15px 40px rgba(0, 255, 65, 0.3),
                0 0 30px rgba(0, 255, 65, 0.1);
            border-color: var(--color-secondary);
        }
        
        .repo-card:hover::before {
            transform: scaleY(1);
        }
        
        .repo-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 15px;
        }
        
        .repo-name {
            font-size: 1.6em;
            font-family: var(--font-futuristic);
            color: var(--color-primary);
            text-decoration: none;
            font-weight: bold;
            text-shadow: 0 0 10px rgba(0, 255, 65, 0.5);
            transition: all 0.3s ease;
        }
        
        .repo-name:hover {
            text-decoration: underline;
            color: var(--color-secondary);
            text-shadow: 0 0 15px rgba(255, 0, 110, 0.8);
        }
        
        .repo-lines {
            font-size: 1.8em;
            font-family: var(--font-futuristic);
            font-weight: bold;
            color: var(--color-primary);
            text-shadow: 0 0 15px rgba(0, 255, 65, 0.6);
        }
        
        .languages {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-top: 15px;
        }
        
        .language-tag {
            background: rgba(0, 255, 65, 0.1);
            padding: 8px 18px;
            border-radius: 20px;
            font-size: 0.9em;
            color: var(--color-primary);
            border: 1px solid var(--color-primary);
            transition: all 0.3s ease;
            position: relative;
        }
        
        .language-tag:hover {
            background: rgba(0, 255, 65, 0.2);
            transform: scale(1.1);
            box-shadow: 0 0 15px rgba(0, 255, 65, 0.4);
        }
        
        .language-percentage-bar {
            margin-top: 5px;
            height: 3px;
            background: var(--color-primary);
            border-radius: 2px;
            box-shadow: 0 0 5px rgba(0, 255, 65, 0.6);
        }
        
        .error {
            background: linear-gradient(135deg, #da3633 0%, #ff0000 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            text-align: center;
            margin: 20px 0;
            display: none;
            border: 2px solid #ff0000;
            box-shadow: 0 0 30px rgba(255, 0, 0, 0.6);
            font-size: 1.1em;
            animation: shake 0.5s;
        }
        
        @keyframes shake {
            0%, 100% { transform: translateX(0); }
            25% { transform: translateX(-10px); }
            75% { transform: translateX(10px); }
        }
        
        .stars {
            color: #f1c40f;
            margin-left: 15px;
            text-shadow: 0 0 10px rgba(241, 196, 15, 0.8);
            font-size: 1.2em;
        }
        
        @media (max-width: 768px) {
            .header h1 {
                font-size: 2.5em;
            }
            
            .big-number {
                font-size: 3.5em;
            }
            
            .input-group {
                flex-direction: column;
            }
            
            .repos-controls {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <canvas id="confetti-canvas"></canvas>
    <div id="matrix-bg"></div>
    <div class="container">
        <div class="header">
            <h1>&lt;GITHUB_CODE_ANALYZER&gt;</h1>
            <p>Decode Your Digital DNA...</p>
        </div>
        
        <div class="search-section">
            <div class="input-group">
                <input type="text" id="username" placeholder="> Enter GitHub username..." />
                <button onclick="analyze()">⚡ ANALYZE ⚡</button>
            </div>
        </div>
        
        <div class="error" id="error"></div>
        
        <div class="loading" id="loading">
            <div class="loading-content">
                <div class="spinner-container">
                    <div class="spinner"></div>
                    <div class="spinner-inner"></div>
                </div>
                <p class="loading-text">SCANNING THE DIGITAL ABYSS...</p>
                <p style="font-size: 0.9em; opacity: 0.7;">This might take a moment</p>
            </div>
        </div>
        
        <div class="results" id="results">
            <div class="stats-overview">
                <div class="big-number" id="totalLines">0</div>
                <div style="font-size: 1.3em; color: #aaa; text-transform: uppercase; letter-spacing: 4px; margin-bottom: 30px;">LINES OF CODE</div>
                
                <div class="milestone-section">
                    <div class="milestone-badge" id="milestoneBadge"></div>
                    <div class="milestone-subtitle" id="milestoneSubtitle"></div>
                    <div class="milestone-fact" id="milestoneFact"></div>
                </div>
                
                <div class="progress-section" id="progressSection" style="display: none;">
                    <div class="progress-label">
                        <span>Progress to Next Milestone</span>
                        <span id="progressPercentage">0%</span>
                    </div>
                    <div class="progress-bar-container">
                        <div class="progress-bar" id="progressBar" style="width: 0%;"></div>
                    </div>
                    <div class="progress-text" id="progressText"></div>
                </div>
            </div>
            
            <div class="language-section" id="languageSection" style="display: none;">
                <h2 class="section-title">> Language Distribution</h2>
                <div class="language-chart" id="languageChart"></div>
            </div>
            
            <div class="funny-stats" id="funnyStats"></div>
            
            <div class="repos-section">
                <h2 class="section-title">> Repository Breakdown</h2>
                <div class="repos-controls">
                    <input type="text" class="search-box" id="repoSearch" placeholder="🔍 Search repositories..." />
                    <select class="sort-select" id="repoSort">
                        <option value="lines-desc">Sort by: Lines (High to Low)</option>
                        <option value="lines-asc">Sort by: Lines (Low to High)</option>
                        <option value="name-asc">Sort by: Name (A-Z)</option>
                        <option value="name-desc">Sort by: Name (Z-A)</option>
                        <option value="stars-desc">Sort by: Stars (High to Low)</option>
                    </select>
                </div>
                <div id="reposList"></div>
            </div>
        </div>
    </div>
    
    <script>
        let allRepos = [];
        let currentDisplayedRepos = [];
        
        // Enhanced Matrix Rain Effect
        function createMatrixRain() {
            const matrixBg = document.getElementById('matrix-bg');
            matrixBg.innerHTML = '';
            const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲンABCDEFGHIJKLMNOPQRSTUVWXYZ';
            const columns = Math.floor(window.innerWidth / 18);
            
            for (let i = 0; i < columns; i++) {
                const column = document.createElement('div');
                column.className = 'matrix-column';
                column.style.left = (i * 18) + 'px';
                column.style.animationDuration = (Math.random() * 4 + 3) + 's';
                column.style.animationDelay = Math.random() * 3 + 's';
                
                let text = '';
                const length = Math.floor(Math.random() * 25) + 15;
                for (let j = 0; j < length; j++) {
                    text += chars[Math.floor(Math.random() * chars.length)] + '<br>';
                }
                column.innerHTML = text;
                
                matrixBg.appendChild(column);
            }
        }
        
        // Confetti Animation
        function createConfetti() {
            const canvas = document.getElementById('confetti-canvas');
            const ctx = canvas.getContext('2d');
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            
            const confetti = [];
            const colors = ['#00ff41', '#ff006e', '#8338ec', '#ffbe0b', '#fb5607'];
            
            for (let i = 0; i < 150; i++) {
                confetti.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height - canvas.height,
                    r: Math.random() * 4 + 2,
                    d: Math.random() * 5 + 2,
                    color: colors[Math.floor(Math.random() * colors.length)],
                    tilt: Math.random() * 10 - 5,
                    tiltAngleIncrement: Math.random() * 0.1 + 0.05,
                    tiltAngle: 0
                });
            }
            
            function draw() {
                ctx.clearRect(0, 0, canvas.width, canvas.height);
                
                confetti.forEach((c, i) => {
                    ctx.beginPath();
                    ctx.lineWidth = c.r;
                    ctx.strokeStyle = c.color;
                    ctx.moveTo(c.x + c.tilt + c.r, c.y);
                    ctx.lineTo(c.x + c.tilt, c.y + c.tilt + c.r);
                    ctx.stroke();
                    
                    c.tiltAngle += c.tiltAngleIncrement;
                    c.y += c.d;
                    c.tilt = Math.sin(c.tiltAngle) * 15;
                    
                    if (c.y > canvas.height) {
                        confetti[i] = {
                            x: Math.random() * canvas.width,
                            y: Math.random() * canvas.height - canvas.height,
                            r: c.r,
                            d: c.d,
                            color: c.color,
                            tilt: Math.random() * 10 - 5,
                            tiltAngleIncrement: c.tiltAngleIncrement,
                            tiltAngle: 0
                        };
                    }
                });
                
                requestAnimationFrame(draw);
            }
            
            draw();
            
            setTimeout(() => {
                canvas.style.opacity = '0';
                setTimeout(() => {
                    canvas.style.display = 'none';
                }, 1000);
            }, 3000);
        }
        
        // Animated Counter
        function animateCounter(element, start, end, duration) {
            const range = end - start;
            const increment = range / (duration / 16);
            let current = start;
            
            const timer = setInterval(() => {
                current += increment;
                if ((increment > 0 && current >= end) || (increment < 0 && current <= end)) {
                    current = end;
                    clearInterval(timer);
                }
                element.textContent = Math.floor(current).toLocaleString();
            }, 16);
        }
        
        // Initialize
        createMatrixRain();
        
        let resizeTimeout;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimeout);
            resizeTimeout = setTimeout(() => {
                createMatrixRain();
                const canvas = document.getElementById('confetti-canvas');
                canvas.width = window.innerWidth;
                canvas.height = window.innerHeight;
            }, 250);
        });
        
        document.getElementById('username').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') analyze();
        });
        
        // Repo search and sort
        document.getElementById('repoSearch').addEventListener('input', function(e) {
            filterAndSortRepos();
        });
        
        document.getElementById('repoSort').addEventListener('change', function(e) {
            filterAndSortRepos();
        });
        
        function filterAndSortRepos() {
            const searchTerm = document.getElementById('repoSearch').value.toLowerCase();
            const sortOption = document.getElementById('repoSort').value;
            
            let filtered = allRepos.filter(repo => 
                repo.name.toLowerCase().includes(searchTerm)
            );
            
            const [sortBy, order] = sortOption.split('-');
            filtered.sort((a, b) => {
                let comparison = 0;
                if (sortBy === 'lines') {
                    comparison = a.lines - b.lines;
                } else if (sortBy === 'name') {
                    comparison = a.name.localeCompare(b.name);
                } else if (sortBy === 'stars') {
                    comparison = a.stars - b.stars;
                }
                return order === 'desc' ? -comparison : comparison;
            });
            
            currentDisplayedRepos = filtered;
            displayRepos(filtered);
        }
        
        function displayRepos(repos) {
            const reposList = document.getElementById('reposList');
            reposList.innerHTML = repos.map(repo => {
                const totalRepoLines = Object.values(repo.languages).reduce((a, b) => a + b, 0);
                return `
                    <div class="repo-card">
                        <div class="repo-header">
                            <a href="${repo.url}" target="_blank" class="repo-name">
                                ${repo.name}
                                ${repo.stars > 0 ? `<span class="stars">⭐ ${repo.stars}</span>` : ''}
                            </a>
                            <div class="repo-lines">${repo.lines.toLocaleString()} lines</div>
                        </div>
                        <div class="languages">
                            ${Object.entries(repo.languages)
                                .sort((a, b) => b[1] - a[1])
                                .map(([lang, size]) => {
                                    const percentage = ((size / totalRepoLines) * 100).toFixed(1);
                                    return `
                                        <div style="display: flex; flex-direction: column; align-items: center;">
                                            <span class="language-tag">
                                                ${lang} <span style="opacity: 0.7;">(${percentage}%)</span>
                                            </span>
                                            <div class="language-percentage-bar" style="width: ${percentage}%;"></div>
                                        </div>
                                    `;
                                }).join('')}
                        </div>
                    </div>
                `;
            }).join('');
        }
        
        async function analyze() {
            const username = document.getElementById('username').value.trim();
            
            if (!username) {
                return;
            }
            
            document.getElementById('error').style.display = 'none';
            document.getElementById('results').style.display = 'none';
            document.getElementById('loading').style.display = 'block';
            
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username })
                });
                
                const data = await response.json();
                
                if (!response.ok) {
                    throw new Error(data.error || 'An error occurred');
                }
                
                displayResults(data);
                createConfetti();
            } catch (error) {
                document.getElementById('error').textContent = error.message;
                document.getElementById('error').style.display = 'block';
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function displayResults(data) {
            // Animated counter for total lines
            const totalLinesEl = document.getElementById('totalLines');
            animateCounter(totalLinesEl, 0, data.total_lines, 2000);
            
            // Milestone
            const badge = document.getElementById('milestoneBadge');
            badge.textContent = data.milestone.title;
            badge.style.background = data.milestone.color;
            badge.style.color = 'white';
            badge.style.borderColor = data.milestone.color;
            
            document.getElementById('milestoneSubtitle').textContent = data.milestone.subtitle;
            document.getElementById('milestoneFact').textContent = data.milestone.fact;
            
            // Progress to next milestone
            if (data.milestone_progress) {
                const progressSection = document.getElementById('progressSection');
                progressSection.style.display = 'block';
                
                setTimeout(() => {
                    const progressBar = document.getElementById('progressBar');
                    progressBar.style.width = data.milestone_progress.percentage + '%';
                    
                    document.getElementById('progressPercentage').textContent = 
                        data.milestone_progress.percentage + '%';
                    document.getElementById('progressText').textContent = 
                        `${data.milestone_progress.remaining.toLocaleString()} lines until next milestone (${data.milestone_progress.next.toLocaleString()} lines)`;
                }, 100);
            }
            
            // Language distribution
            if (data.language_distribution && data.language_distribution.length > 0) {
                const languageSection = document.getElementById('languageSection');
                languageSection.style.display = 'block';
                
                const languageChart = document.getElementById('languageChart');
                languageChart.innerHTML = data.language_distribution.map(lang => `
                    <div class="language-item">
                        <div class="language-name">${lang.name}</div>
                        <div class="language-bar-container">
                            <div class="language-bar" style="width: 0%;" data-width="${lang.percentage}%"></div>
                        </div>
                        <div class="language-percentage">${lang.percentage}%</div>
                    </div>
                `).join('');
                
                // Animate language bars
                setTimeout(() => {
                    document.querySelectorAll('.language-bar').forEach(bar => {
                        bar.style.width = bar.getAttribute('data-width');
                    });
                }, 500);
            }
            
            // Funny stats
            const funnyStats = document.getElementById('funnyStats');
            funnyStats.innerHTML = data.funny_stats.map((stat, index) => `
                <div class="stat-card" style="animation-delay: ${index * 0.1}s;">
                    <div class="stat-icon">${stat.icon}</div>
                    <div class="stat-value">${stat.value}</div>
                    <div class="stat-label">${stat.label}</div>
                </div>
            `).join('');
            
            // Repos
            allRepos = data.repos;
            currentDisplayedRepos = data.repos;
            displayRepos(data.repos);
            
            document.getElementById('results').style.display = 'block';
            
            // Smooth scroll to results
            setTimeout(() => {
                document.getElementById('results').scrollIntoView({ 
                    behavior: 'smooth', 
                    block: 'start' 
                });
            }, 100);
        }
    </script>
</body>
</html>'''
    
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("✨ GitHub Code Analyzer is starting...")
    print("🌐 Open your browser and go to: http://127.0.0.1:5000")
    print("🚀 Press Ctrl+C to stop the server")
    app.run(debug=True, port=5000)
