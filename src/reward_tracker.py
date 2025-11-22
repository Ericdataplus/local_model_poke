"""
Reward system for Pokemon Crystal AI.
Tracks progress and provides feedback on exploration and achievements.
"""

class RewardTracker:
    def __init__(self):
        self.visited_tiles = set()  # (map_group, map_number, x, y)
        self.visited_maps = set()  # (map_group, map_number)
        self.total_steps = 0
        self.last_position = None
        self.last_badges = 0
        self.last_party_count = 0
        self.last_pokedex_owned = 0
        self.rewards = []
        
    def update(self, game_state):
        """
        Update tracker with current game state and calculate rewards.
        Returns a reward message if any rewards were earned.
        """
        rewards_earned = []
        
        # Extract current state
        player = game_state['player']
        current_pos = (player['map_group'], player['map_number'], player['x'], player['y'])
        current_map = (player['map_group'], player['map_number'])
        
        # REWARD: New tile discovered
        if current_pos not in self.visited_tiles:
            self.visited_tiles.add(current_pos)
            rewards_earned.append({
                'type': 'NEW_TILE',
                'points': 1,
                'message': f"🗺️ New tile discovered! ({player['x']}, {player['y']})"
            })
        
        # REWARD: New map discovered
        if current_map not in self.visited_maps:
            self.visited_maps.add(current_map)
            rewards_earned.append({
                'type': 'NEW_MAP',
                'points': 50,
                'message': f"🌍 NEW MAP DISCOVERED! Map ({player['map_group']}, {player['map_number']})"
            })
        
        # REWARD: Movement (step count)
        if self.last_position and self.last_position != current_pos:
            self.total_steps += 1
            # Milestone rewards every 100 steps
            if self.total_steps % 100 == 0:
                rewards_earned.append({
                    'type': 'STEP_MILESTONE',
                    'points': 10,
                    'message': f"🚶 {self.total_steps} steps taken!"
                })
        
        # REWARD: New badge
        current_badges = game_state['badges']['total']
        if current_badges > self.last_badges:
            badges_gained = current_badges - self.last_badges
            rewards_earned.append({
                'type': 'BADGE',
                'points': 500 * badges_gained,
                'message': f"🏆 BADGE EARNED! Total: {current_badges}/16"
            })
            self.last_badges = current_badges
        
        # REWARD: New Pokemon in party
        current_party = game_state['party']['count']
        if current_party > self.last_party_count:
            pokemon_gained = current_party - self.last_party_count
            rewards_earned.append({
                'type': 'POKEMON',
                'points': 100 * pokemon_gained,
                'message': f"⚡ NEW POKEMON! Party size: {current_party}"
            })
            self.last_party_count = current_party
        
        # REWARD: New Pokedex entry
        current_owned = game_state['pokedex']['owned']
        if current_owned > self.last_pokedex_owned:
            new_entries = current_owned - self.last_pokedex_owned
            rewards_earned.append({
                'type': 'POKEDEX',
                'points': 25 * new_entries,
                'message': f"📖 Pokedex updated! {current_owned} owned"
            })
            self.last_pokedex_owned = current_owned
        
        # Update last position
        self.last_position = current_pos
        
        # Store rewards
        self.rewards.extend(rewards_earned)
        
        return rewards_earned
    
    def get_stats(self):
        """Get current exploration statistics."""
        total_points = sum(r['points'] for r in self.rewards)
        
        return {
            'total_tiles_discovered': len(self.visited_tiles),
            'total_maps_discovered': len(self.visited_maps),
            'total_steps': self.total_steps,
            'total_points': total_points,
            'recent_rewards': self.rewards[-5:] if self.rewards else []
        }
    
    def format_stats_for_ai(self):
        """Format stats as a motivational message for the AI."""
        stats = self.get_stats()
        
        lines = []
        lines.append("## 🎯 Progress & Rewards")
        lines.append("")
        lines.append(f"**Exploration Score:** {stats['total_points']} points")
        lines.append(f"**Tiles Discovered:** {stats['total_tiles_discovered']}")
        lines.append(f"**Maps Explored:** {stats['total_maps_discovered']}")
        lines.append(f"**Steps Taken:** {stats['total_steps']}")
        
        if stats['recent_rewards']:
            lines.append("")
            lines.append("**Recent Achievements:**")
            for reward in stats['recent_rewards']:
                lines.append(f"  - {reward['message']} (+{reward['points']} pts)")
        
        lines.append("")
        lines.append("💡 **Keep exploring to earn more points!**")
        lines.append("")
        
        return "\n".join(lines)
