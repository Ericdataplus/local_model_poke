"""
Comprehensive Pokemon Crystal RAM reader.
Extracts ALL useful game state information for the AI.
Based on Pokemon Crystal disassembly and WRAM documentation.
"""

def read_complete_game_state(pyboy):
    """
    Read EVERYTHING useful from Pokemon Crystal RAM.
    Returns a comprehensive dictionary of game state.
    """
    state = {}
    
    # ===== PLAYER DATA =====
    state['player'] = {
        'x': pyboy.memory[0xDCB8],  # X coordinate
        'y': pyboy.memory[0xDCB7],  # Y coordinate
        'map_group': pyboy.memory[0xDCB5],  # Map bank/group
        'map_number': pyboy.memory[0xDCB6],  # Map number
        'facing': get_facing_direction(pyboy.memory[0xDCBB]),  # Direction facing
    }
    
    # ===== MAP DATA =====
    state['map'] = {
        'width': pyboy.memory[0xD4B1],
        'height': pyboy.memory[0xD4B2],
        'warp_count': pyboy.memory[0xD4B6],
        'object_count': pyboy.memory[0xD4CE],  # NPCs/objects on map
    }
    
    # ===== COLLISION DATA (CRITICAL FOR NAVIGATION) =====
    state['collision'] = {
        'down': pyboy.memory[0xC2FA],
        'up': pyboy.memory[0xC2FB],
        'left': pyboy.memory[0xC2FC],
        'right': pyboy.memory[0xC2FD],
        'down_walkable': pyboy.memory[0xC2FA] == 0x00,
        'up_walkable': pyboy.memory[0xC2FB] == 0x00,
        'left_walkable': pyboy.memory[0xC2FC] == 0x00,
        'right_walkable': pyboy.memory[0xC2FD] == 0x00,
    }
    
    # ===== PARTY DATA =====
    party_count = pyboy.memory[0xDCD7]
    state['party'] = {
        'count': party_count,
        'pokemon': []
    }
    
    # Read first Pokemon in party (if exists)
    if party_count > 0:
        try:
            # Party Pokemon 1 data starts at 0xDCD8
            base = 0xDCD8
            pokemon1 = {
                'species': pyboy.memory[base],
                'hp_current': (pyboy.memory[base + 0x22] << 8) | pyboy.memory[base + 0x23],
                'hp_max': (pyboy.memory[base + 0x24] << 8) | pyboy.memory[base + 0x25],
                'level': pyboy.memory[base + 0x1F],
                'status': pyboy.memory[base + 0x20],  # 0=healthy, non-zero=status condition
            }
            state['party']['pokemon'].append(pokemon1)
        except:
            pass
    
    # ===== BATTLE STATE =====
    state['battle'] = {
        'in_battle': pyboy.memory[0xD057] != 0,  # wIsInBattle flag
        'battle_type': pyboy.memory[0xD057],
    }
    
    # ===== MONEY =====
    try:
        # Money is stored as BCD (Binary Coded Decimal) - 3 bytes
        money_byte1 = pyboy.memory[0xD84E]
        money_byte2 = pyboy.memory[0xD84F]
        money_byte3 = pyboy.memory[0xD850]
        # Convert BCD to decimal
        state['money'] = (
            ((money_byte1 >> 4) * 100000) + ((money_byte1 & 0x0F) * 10000) +
            ((money_byte2 >> 4) * 1000) + ((money_byte2 & 0x0F) * 100) +
            ((money_byte3 >> 4) * 10) + (money_byte3 & 0x0F)
        )
    except:
        state['money'] = 0
    
    # ===== BADGES =====
    try:
        # Johto badges at 0xD857, Kanto badges at 0xD858
        johto_badges = pyboy.memory[0xD857]
        kanto_badges = pyboy.memory[0xD858]
        state['badges'] = {
            'johto': bin(johto_badges).count('1'),  # Count set bits
            'kanto': bin(kanto_badges).count('1'),
            'total': bin(johto_badges).count('1') + bin(kanto_badges).count('1')
        }
    except:
        state['badges'] = {'johto': 0, 'kanto': 0, 'total': 0}
    
    # ===== PLAY TIME =====
    try:
        # Play time in frames (60 frames = 1 second)
        hours = pyboy.memory[0xD4C3]
        minutes = pyboy.memory[0xD4C4]
        seconds = pyboy.memory[0xD4C5]
        state['playtime'] = {
            'hours': hours,
            'minutes': minutes,
            'seconds': seconds,
            'formatted': f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        }
    except:
        state['playtime'] = {'hours': 0, 'minutes': 0, 'seconds': 0, 'formatted': "00:00:00"}
    
    # ===== GAME SETTINGS =====
    try:
        options = pyboy.memory[0xD3D5]
        state['settings'] = {
            'battle_scene': 'ON' if (options & 0x01) == 0 else 'OFF',
            'battle_style': 'SHIFT' if (options & 0x02) == 0 else 'SET',
            'sound': 'MONO' if (options & 0x04) == 0 else 'STEREO',
            'text_speed': (options >> 3) & 0x07,  # Bits 3-7
        }
    except:
        state['settings'] = {}
    
    # ===== ITEMS (first few from bag) =====
    try:
        # Items pocket starts at 0xD892
        item_count = pyboy.memory[0xD892]
        state['items'] = {
            'count': item_count,
            'first_items': []
        }
        # Read first 3 items
        for i in range(min(item_count, 3)):
            item_id = pyboy.memory[0xD893 + (i * 2)]
            item_qty = pyboy.memory[0xD894 + (i * 2)]
            state['items']['first_items'].append({'id': item_id, 'quantity': item_qty})
    except:
        state['items'] = {'count': 0, 'first_items': []}
    
    # ===== POKEDEX =====
    try:
        # Pokedex seen/owned counts
        state['pokedex'] = {
            'seen': pyboy.memory[0xDE99],
            'owned': pyboy.memory[0xDE9A],
        }
    except:
        state['pokedex'] = {'seen': 0, 'owned': 0}
    
    # ===== CURRENT MENU/STATE =====
    try:
        state['menu_state'] = {
            'in_menu': pyboy.memory[0xD0A0] != 0,  # wMenuCursorY
            'cursor_y': pyboy.memory[0xD0A0],
            'cursor_x': pyboy.memory[0xD0A1],
        }
    except:
        state['menu_state'] = {}

    # ===== DIALOGUE STATE =====
    try:
        # wTextBoxFlags at 0xCFA7. Bit 0 usually indicates text box open.
        text_box_flags = pyboy.memory[0xCFA7]
        state['dialogue'] = {
            'is_open': (text_box_flags & 0x01) != 0,
            'flags': text_box_flags
        }
    except:
        state['dialogue'] = {'is_open': False, 'flags': 0}
    
    return state


def get_facing_direction(direction_byte):
    """Convert direction byte to human-readable string."""
    directions = {
        0x00: "DOWN",
        0x04: "UP",
        0x08: "LEFT",
        0x0C: "RIGHT",
        0x01: "DOWN",  # Movement variants
        0x05: "UP",
        0x09: "LEFT",
        0x0D: "RIGHT",
        0x1F: "STANDING"
    }
    return directions.get(direction_byte, f"UNKNOWN(0x{direction_byte:02X})")


def format_game_state_for_ai(state):
    """
    Format the complete game state into a readable string for the AI.
    """
    lines = []
    
    lines.append("## Complete Game State")
    lines.append("")
    
    # Player info
    p = state['player']
    lines.append(f"**Position:** ({p['x']}, {p['y']}) facing {p['facing']}")
    lines.append(f"**Map:** Group {p['map_group']}, Number {p['map_number']}")
    lines.append("")
    
    # Party
    if state['party']['count'] > 0:
        lines.append(f"**Party:** {state['party']['count']} Pokemon")
        if state['party']['pokemon']:
            p1 = state['party']['pokemon'][0]
            lines.append(f"  - Lead: Species #{p1['species']}, Lv.{p1['level']}, HP: {p1['hp_current']}/{p1['hp_max']}")
    else:
        lines.append("**Party:** No Pokemon")
    lines.append("")
    
    # Progress
    lines.append(f"**Badges:** {state['badges']['total']} (Johto: {state['badges']['johto']}, Kanto: {state['badges']['kanto']})")
    lines.append(f"**Money:** ${state['money']}")
    lines.append(f"**Pokedex:** {state['pokedex']['owned']} owned, {state['pokedex']['seen']} seen")
    lines.append(f"**Playtime:** {state['playtime']['formatted']}")
    lines.append("")
    
    # Battle state
    if state['battle']['in_battle']:
        lines.append("**STATUS:** IN BATTLE!")
    
    # Dialogue state
    if state.get('dialogue', {}).get('is_open', False):
        lines.append("**STATUS:** DIALOGUE BOX OPEN! Press 'A' to advance.")
        
    lines.append("")
    
    # Items
    if state['items']['count'] > 0:
        lines.append(f"**Items:** {state['items']['count']} in bag")
        for item in state['items']['first_items']:
            lines.append(f"  - Item #{item['id']} x{item['quantity']}")
    lines.append("")
    
    return "\n".join(lines)
