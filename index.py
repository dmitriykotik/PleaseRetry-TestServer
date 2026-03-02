import socket
import struct
from protobufs import csgo_pb2

# Listen settings
IP = '127.0.0.1' # IP
PORT = 27010     # Port

# Account Id
ACCOUNT_ID = 116072338 # SteamId (32)

# Matchmaking
RANK = 0  # Matchmaking Rank (0-18)
WINS = 0  # Matchmaking Wins

LEVEL = 1 # Level (1-40)
XP = 0    # Experience (0-5000)

# Punishments
VAC_BANNED = 0      # Is there a VAC lock? (0-1) (See documentation)
PENALTY_REASON = -1 # Are there any other types of punishment? (0-12) (See documentation)
PENALTY_SECONDS = 0 # Time remaining until the end of the punishment in seconds

# Likes
FRIENDLY = 0 # Likes for the item "friendly"
TEACHING = 0 # Likes for the item "teaching"
LEADER = 0   # Likes for the item "leader"

def patch(data):
    gc_header = data[:8]
    pb_payload = data[8:] 
    
    msg = csgo_pb2.MatchmakingHello()
    msg.ParseFromString(pb_payload)
    
    msg.account_id = ACCOUNT_ID
    
    msg.ranking.account_id = ACCOUNT_ID
    msg.ranking.rank_id = RANK
    msg.ranking.wins = WINS
    msg.ranking.rank_type_id = 6

    msg.player_level = LEVEL
    msg.player_cur_xp = XP

    msg.vac_banned = VAC_BANNED
    
    if PENALTY_REASON != -1:
        msg.penalty_reason = PENALTY_REASON
        msg.penalty_seconds = PENALTY_SECONDS
    
    msg.commendation.cmd_friendly = FRIENDLY
    msg.commendation.cmd_teaching = TEACHING
    msg.commendation.cmd_leader = LEADER

    return gc_header + msg.SerializeToString()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((IP, PORT))
    server.listen(1)
    print(" - - - Server Launched - - -")

    while True:
        conn, addr = server.accept()
        try:
            while True:
                header = conn.recv(8)
                if not header: break
                m_type, m_size = struct.unpack('<II', header)
                data = conn.recv(m_size)
                
                raw_type = m_type & 0x7FFFFFFF
                if raw_type == 9110:
                    print(f"[!] Substitution 9110")
                    patched_data = smart_patch(data)
                    
                    h = struct.pack('<II', 9110 | 0x80000000, len(patched_data))
                    conn.sendall(h + patched_data)
                    
                    update_payload = b"\x91\x23\x00\x80\x00\x00\x00\x00\x08\x12"
                    h2 = struct.pack('<II', 9105 | 0x80000000, len(update_payload))
                    conn.sendall(h2 + update_payload)
                else:
                    print(raw_type)
                    conn.sendall(header + data)
        except Exception as e: 
            pass
        finally: 
            conn.close()

if __name__ == "__main__":
    start_server()