import pygame
import random
import time
import math

# ==========================================
# 1. SYSTEM CONFIGURATION & CONSTANTS
# ==========================================
WIDTH, HEIGHT = 1600, 900
SIM_W, SIM_H = 1100, 900
UI_W = WIDTH - SIM_W

# Colors
C_BG = (15, 15, 20)
C_ROAD = (50, 54, 57)
C_GRASS = (39, 110, 54)
C_SIDEWALK = (140, 145, 150)
C_MARKING = (220, 230, 235)
C_YELLOW_LINE = (241, 196, 15)
C_BUILDING_BASE = (60, 65, 70)
C_UI_BG = (10, 12, 15)
C_ACCENT = (0, 255, 150)
C_HACKER_GREEN = (0, 200, 50)

# Geometry
CX, CY = SIM_W // 2, SIM_H // 2
LANE_W = 35
ROAD_W = LANE_W * 4  # 4 Lanes per road (2 incoming, 2 outgoing)

# ==========================================
# 2. CYBER INTRO SCREEN
# ==========================================
class IntroScreen:
    def __init__(self, screen):
        self.screen = screen
        self.font_large = pygame.font.SysFont("Courier New", 80, bold=True)
        self.font_small = pygame.font.SysFont("Courier New", 18)
        self.start_time = time.time()
        self.target_text = "SHOCK THE SYSTEM"
        self.current_text = ""
        self.char_index = 0
        self.matrix_drops = [[random.randint(0, WIDTH), random.randint(-500, 0), random.uniform(2, 6)] for _ in range(100)]

    def update_and_draw(self):
        elapsed = time.time() - self.start_time
        self.screen.fill((5, 5, 5))

        for drop in self.matrix_drops:
            char = chr(random.randint(33, 126))
            char_surface = self.font_small.render(char, True, (0, random.randint(100, 255), 0))
            self.screen.blit(char_surface, (drop[0], drop[1]))
            drop[1] += drop[2]
            if drop[1] > HEIGHT:
                drop[1] = random.randint(-50, 0)
                drop[0] = random.randint(0, WIDTH)

        if self.char_index < len(self.target_text):
            if int(elapsed * 15) > self.char_index:
                self.char_index += 1
                self.current_text = self.target_text[:self.char_index]

        glitch_x = random.choice([-3, 0, 3]) if random.random() < 0.1 else 0
        glitch_y = random.choice([-3, 0, 3]) if random.random() < 0.1 else 0

        text_surface = self.font_large.render(self.current_text, True, C_ACCENT)
        text_rect = text_surface.get_rect(center=(WIDTH // 2 + glitch_x, HEIGHT // 2 + glitch_y))
        self.screen.blit(text_surface, text_rect)

        if time.time() % 0.5 < 0.25 and self.char_index >= len(self.target_text):
            cursor = self.font_large.render("_", True, C_ACCENT)
            self.screen.blit(cursor, (text_rect.right + 5, text_rect.top))

        if elapsed > 1.0:
            sys_text = self.font_small.render("SYSTEM BOOT SEQUENCE INITIATED...", True, C_HACKER_GREEN)
            self.screen.blit(sys_text, (WIDTH // 2 - sys_text.get_width() // 2, HEIGHT // 2 + 60))
        if elapsed > 2.0:
            bypass_text = self.font_small.render("BYPASSING SECURITY PROTOCOLS... OK", True, C_HACKER_GREEN)
            self.screen.blit(bypass_text, (WIDTH // 2 - bypass_text.get_width() // 2, HEIGHT // 2 + 90))

        return elapsed > 3.5

# ==========================================
# 3. VEHICLE & KINEMATICS SYSTEM
# ==========================================
class Vehicle:
    TYPES = {
        "car": {"len": 40, "wid": 20, "spd": 5.0, "accel": 0.1, "brake": 0.3, "clr": (64, 156, 255)},
        "bus": {"len": 80, "wid": 26, "spd": 3.0, "accel": 0.05, "brake": 0.15, "clr": (255, 165, 0)},
        "truck": {"len": 70, "wid": 24, "spd": 2.5, "accel": 0.04, "brake": 0.15, "clr": (180, 180, 180)},
        "bike": {"len": 20, "wid": 10, "spd": 6.5, "accel": 0.15, "brake": 0.4, "clr": (255, 200, 50)},
        "ambulance": {"len": 45, "wid": 22, "spd": 7.5, "accel": 0.12, "brake": 0.35, "clr": (245, 245, 245)}
    }

    def __init__(self, axis, direction, lane_idx, v_type):
        self.axis = axis
        self.dir = direction
        self.lane_idx = lane_idx
        self.type = v_type
        
        stats = self.TYPES[v_type]
        self.length = stats["len"]
        self.width = stats["wid"]
        self.max_speed = stats["spd"]
        self.accel = stats["accel"]
        self.brake = stats["brake"]
        self.color = stats["clr"]
        
        if self.axis == "NS":
            self.w, self.h = self.width, self.length
        else:
            self.w, self.h = self.length, self.width
            
        self.speed = self.max_speed
        self.is_emergency = (v_type == "ambulance")
        self.wait_time = 0
        self.passed_intersection = False

        self._initialize_position()
        self._generate_sprite()

    def _initialize_position(self):
        offset = (self.lane_idx * LANE_W) + (LANE_W / 2)
        if self.axis == "NS":
            self.x = CX - ROAD_W//2 + offset if self.dir == 1 else CX + ROAD_W//2 - offset
            self.x -= self.w // 2
            self.y = -self.h - 50 if self.dir == 1 else SIM_H + 50
        else:
            self.y = CY - ROAD_W//2 + offset if self.dir == -1 else CY + ROAD_W//2 - offset
            self.y -= self.h // 2
            self.x = SIM_W + 50 if self.dir == -1 else -self.w - 50

    def _generate_sprite(self):
        surf = pygame.Surface((self.width, self.length), pygame.SRCALPHA)
        pygame.draw.rect(surf, self.color, (0, 0, self.width, self.length), border_radius=3)
        
        if self.type == "car":
            pygame.draw.rect(surf, (30, 30, 30), (2, 8, self.width-4, 8), border_radius=2)
            pygame.draw.rect(surf, (30, 30, 30), (2, self.length-14, self.width-4, 6), border_radius=2)
        elif self.type == "bus":
            for y in range(10, self.length-10, 12):
                pygame.draw.rect(surf, (200, 220, 255), (2, y, self.width-4, 8))
        elif self.type == "truck":
            pygame.draw.rect(surf, (150, 150, 150), (0, 0, self.width, 18), border_radius=2)
            pygame.draw.rect(surf, (30, 30, 30), (0, 18, self.width, 2))
        elif self.type == "bike":
            pygame.draw.circle(surf, (50, 50, 50), (self.width//2, self.length//2), 4)
        elif self.type == "ambulance":
            pygame.draw.rect(surf, (255, 0, 0), (self.width//2-2, self.length//2-8, 4, 16))
            pygame.draw.rect(surf, (255, 0, 0), (self.width//2-8, self.length//2-2, 16, 4))

        angle = 0
        if self.axis == "NS": angle = 180 if self.dir == 1 else 0
        else: angle = -90 if self.dir == 1 else 90

        self.sprite = pygame.transform.rotate(surf, angle)

    def draw(self, screen):
        screen.blit(self.sprite, (self.x, self.y))
        if self.is_emergency and (time.time() % 0.3 < 0.15):
            s = pygame.Surface((self.w, self.h), pygame.SRCALPHA)
            s.fill((0, 100, 255, 100))
            screen.blit(s, (self.x, self.y))

    def get_front_bumper(self):
        if self.axis == "NS": return self.y + self.h if self.dir == 1 else self.y
        else: return self.x + self.w if self.dir == 1 else self.x

    def get_back_bumper(self):
        if self.axis == "NS": return self.y if self.dir == 1 else self.y + self.h
        else: return self.x if self.dir == 1 else self.x + self.w

# ==========================================
# 4. TRAFFIC SIGNAL & AI CONTROLLER
# ==========================================
class TrafficController:
    def __init__(self):
        self.signals = {"NS": "RED", "EW": "GREEN"}
        self.timer = 10.0
        self.transitioning = False
        self.target_axis = None
        self.reason = "SYSTEM INITIALIZATION"

    def update(self, vehicles, dt):
        self.timer -= dt
        if self.transitioning:
            if self.timer <= 0:
                self.signals = {"NS": "RED", "EW": "RED"}
                self.signals[self.target_axis] = "GREEN"
                self.transitioning = False
                self.timer = 8.0
            return

        if self.timer > 0: return

        ns_score, ns_emg = self._evaluate_axis(vehicles, "NS")
        ew_score, ew_emg = self._evaluate_axis(vehicles, "EW")

        active = "NS" if self.signals["NS"] == "GREEN" else "EW"
        inactive = "EW" if active == "NS" else "NS"

        if (ns_emg > 0 and inactive == "NS") or (ew_emg > 0 and inactive == "EW"):
            axis = "NORTH-SOUTH" if ns_emg > 0 else "EAST-WEST"
            self._switch("NS" if ns_emg > 0 else "EW", f"EMERGENCY PRIORITY - {axis}")
        elif (ns_score > ew_score + 10 and inactive == "NS"):
            self._switch("NS", "CONGESTION OVERRIDE: NORTH-SOUTH")
        elif (ew_score > ns_score + 10 and inactive == "EW"):
            self._switch("EW", "CONGESTION OVERRIDE: EAST-WEST")
        else:
            self.reason = "MAINTAINING FLOW: STABLE DENSITY"
            self.timer = 3.0

    def _evaluate_axis(self, vehicles, axis):
        waiting = [v for v in vehicles if v.axis == axis and not v.passed_intersection and v.speed < 0.5]
        count_score = len(waiting) * 2
        wait_score = sum(v.wait_time for v in waiting) * 0.5
        emg = sum(1 for v in vehicles if v.axis == axis and not v.passed_intersection and v.is_emergency)
        return count_score + wait_score, emg

    def _switch(self, target, reason):
        self.signals = {"NS": "YELLOW", "EW": "YELLOW"}
        self.transitioning = True
        self.target_axis = target
        self.timer = 2.0
        self.reason = reason

# ==========================================
# 5. ENVIRONMENT RENDERER
# ==========================================
class Environment:
    def __init__(self, screen):
        self.screen = screen
        self.bg_cache = pygame.Surface((SIM_W, SIM_H))
        self._build_static_environment()

    def _draw_buildings_in_quadrant(self, qx, qy, qw, qh):
        pad = 25
        bx, by = qx + pad, qy + pad
        bw, bh = qw - pad*2, qh - pad*2
        if bw <= 0 or bh <= 0: return
        pygame.draw.rect(self.bg_cache, C_BUILDING_BASE, (bx, by, bw, bh), border_radius=8)
        random.seed(int(bx * by)) 
        colors = [(45, 50, 55), (55, 60, 65), (65, 70, 75), (40, 45, 50)]
        for x in range(int(bx) + 15, int(bx + bw - 50), 75):
            for y in range(int(by) + 15, int(by + bh - 50), 75):
                if random.random() < 0.85:
                    w, h = random.randint(45, 65), random.randint(45, 65)
                    b_color = random.choice(colors)
                    pygame.draw.rect(self.bg_cache, b_color, (x, y, w, h), border_radius=4)
                    for wx in range(x + 6, x + w - 10, 14):
                        for wy in range(y + 6, y + h - 10, 14):
                            if random.random() < 0.6: 
                                pygame.draw.rect(self.bg_cache, (210, 230, 180), (wx, wy, 5, 7))
                            else: 
                                pygame.draw.rect(self.bg_cache, (20, 25, 30), (wx, wy, 5, 7))

    def _build_static_environment(self):
        self.bg_cache.fill(C_GRASS)
        pygame.draw.rect(self.bg_cache, C_ROAD, (0, CY - ROAD_W//2, SIM_W, ROAD_W))
        pygame.draw.rect(self.bg_cache, C_ROAD, (CX - ROAD_W//2, 0, ROAD_W, SIM_H))
        sw = 15
        pygame.draw.rect(self.bg_cache, C_SIDEWALK, (0, CY - ROAD_W//2 - sw, SIM_W, sw))
        pygame.draw.rect(self.bg_cache, C_SIDEWALK, (0, CY + ROAD_W//2, SIM_W, sw))
        pygame.draw.rect(self.bg_cache, C_SIDEWALK, (CX - ROAD_W//2 - sw, 0, sw, SIM_H))
        pygame.draw.rect(self.bg_cache, C_SIDEWALK, (CX + ROAD_W//2, 0, sw, SIM_H))
        pygame.draw.rect(self.bg_cache, C_ROAD, (CX - ROAD_W//2 - sw, CY - ROAD_W//2, ROAD_W + sw*2, ROAD_W))
        self._draw_dashed_line((0, CY), (SIM_W, CY), C_YELLOW_LINE, double=True)
        self._draw_dashed_line((CX, 0), (CX, SIM_H), C_YELLOW_LINE, double=True)
        for offset in [-LANE_W, LANE_W]:
            self._draw_dashed_line((0, CY + offset), (SIM_W, CY + offset), C_MARKING)
            self._draw_dashed_line((CX + offset, 0), (CX + offset, SIM_H), C_MARKING)
        z_dist = ROAD_W//2 + 5
        self._draw_zebra(CX, CY - z_dist, True)
        self._draw_zebra(CX, CY + z_dist, True)
        self._draw_zebra(CX - z_dist, CY, False)
        self._draw_zebra(CX + z_dist, CY, False)
        rw2 = ROAD_W // 2 + 10 
        self._draw_buildings_in_quadrant(0, 0, CX - rw2, CY - rw2)
        self._draw_buildings_in_quadrant(CX + rw2, 0, SIM_W - (CX + rw2), CY - rw2)
        self._draw_buildings_in_quadrant(0, CY + rw2, CX - rw2, SIM_H - (CY + rw2))
        self._draw_buildings_in_quadrant(CX + rw2, CY + rw2, SIM_W - (CX + rw2), SIM_H - (CY + rw2))
        random.seed()

    def _draw_dashed_line(self, p1, p2, color, double=False):
        pygame.draw.line(self.bg_cache, color, p1, p2, 2 if not double else 4)

    def _draw_zebra(self, x, y, horizontal):
        w, h = (ROAD_W, 15) if horizontal else (15, ROAD_W)
        px, py = x - w//2, y - h//2
        pygame.draw.rect(self.bg_cache, C_MARKING, (px, py, w, h))

    def render(self):
        self.screen.blit(self.bg_cache, (0,0))

    def render_signals(self, signals, timer):
        poles = {
            "NS": [(CX - ROAD_W//2 - 20, CY + ROAD_W//2 + 10), (CX + ROAD_W//2 + 10, CY - ROAD_W//2 - 40)],
            "EW": [(CX - ROAD_W//2 - 40, CY - ROAD_W//2 - 20), (CX + ROAD_W//2 + 10, CY + ROAD_W//2 + 10)]
        }
        font = pygame.font.SysFont("Consolas", 14, bold=True)
        for axis, state in signals.items():
            for px, py in poles[axis]:
                pygame.draw.rect(self.screen, (30,30,30), (px, py, 20, 50), border_radius=4)
                c_red = (255,0,0) if state in ["RED", "YELLOW"] else (50,0,0)
                c_yel = (255,200,0) if state == "YELLOW" else (50,50,0)
                c_grn = (0,255,0) if state == "GREEN" else (0,50,0)
                pygame.draw.circle(self.screen, c_red, (px+10, py+10), 6)
                pygame.draw.circle(self.screen, c_yel, (px+10, py+25), 6)
                pygame.draw.circle(self.screen, c_grn, (px+10, py+40), 6)
                if state in ["GREEN", "YELLOW"]:
                    tm_txt = font.render(f"{max(0, timer):.1f}", True, (255,255,255))
                    self.screen.blit(tm_txt, (px - 5, py - 15))

# ==========================================
# 6. MAIN SIMULATION ENGINE
# ==========================================
class SimulationApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Professional Urban AI Traffic Sim")
        self.clock = pygame.time.Clock()
        self.env = Environment(self.screen)
        self.ai = TrafficController()
        self.intro = IntroScreen(self.screen)
        self.vehicles = []
        self.state = "INTRO"
        self.status = "RUNNING"
        self.speed_mult = 1.0
        self.f_big = pygame.font.SysFont("Courier New", 55, bold=True)
        self.f_sys = pygame.font.SysFont("Consolas", 18, bold=True)
        self.f_sys_sm = pygame.font.SysFont("Consolas", 14)

    def process_vehicles(self, dt):
        stop_lines = {
            "NS": {1: CY - ROAD_W//2 - 10, -1: CY + ROAD_W//2 + 10},
            "EW": {1: CX - ROAD_W//2 - 10, -1: CX + ROAD_W//2 + 10}
        }

        for v in self.vehicles:
            target_spd = v.max_speed * self.speed_mult
            front = v.get_front_bumper()

            # 1. Traffic Light Logic
            if not v.passed_intersection:
                sl = stop_lines[v.axis][v.dir]
                dist_to_light = (sl - front) * v.dir
                if dist_to_light < 0:
                    v.passed_intersection = True
                elif dist_to_light < 80 and self.ai.signals[v.axis] != "GREEN":
                    if dist_to_light < 15: target_spd = 0
                    else: target_spd = min(target_spd, max(0, dist_to_light * 0.05))

            # 2. FIXED: Strict Anti-Overlap / Bounding Box Collision
            v_rect = pygame.Rect(v.x, v.y, v.w, v.h)
            look_dist = 45 if v.type == "bike" else 35 # Bikes need more reaction gap
            
            look_rect = v_rect.copy()
            if v.axis == "NS":
                if v.dir == 1: look_rect.height += look_dist
                else: look_rect.y -= look_dist; look_rect.height += look_dist
            else:
                if v.dir == 1: look_rect.width += look_dist
                else: look_rect.x -= look_dist; look_rect.width += look_dist

            obstacle_found = False
            for o in self.vehicles:
                if o == v: continue
                o_rect = pygame.Rect(o.x, o.y, o.w, o.h)
                
                if look_rect.colliderect(o_rect):
                    in_front = False
                    # Lane check: must be in same lane (center points roughly align)
                    if v.axis == "NS" and abs(v.x - o.x) < 10:
                        if (v.dir == 1 and o.y > v.y) or (v.dir == -1 and o.y < v.y): in_front = True
                    elif v.axis == "EW" and abs(v.y - o.y) < 10:
                        if (v.dir == 1 and o.x > v.x) or (v.dir == -1 and o.x < v.x): in_front = True
                        
                    if in_front:
                        obstacle_found = True
                        # Get exact gap to trigger Hard Stop
                        if v.axis == "NS": gap = abs(o.y - v.y) - (v.h/2 + o.h/2)
                        else: gap = abs(o.x - v.x) - (v.w/2 + o.w/2)
                        
                        if gap < 10: # Hard stop distance
                            target_spd = 0
                            v.speed = min(v.speed, 0.5)
                        else:
                            target_spd = min(target_spd, o.speed * 0.95)
                        break

            # 3. Kinematics
            if v.speed > target_spd: v.speed = max(target_spd, v.speed - v.brake * self.speed_mult)
            elif v.speed < target_spd: v.speed = min(target_spd, v.speed + v.accel * self.speed_mult)
            if v.speed < 0.05: v.speed = 0
            if v.speed == 0 and not v.passed_intersection: v.wait_time += dt
            
            if v.axis == "NS": v.y += v.speed * v.dir
            else: v.x += v.speed * v.dir

    def spawn_traffic(self):
        if random.random() < 0.04 * self.speed_mult and len(self.vehicles) < 100:
            axis = random.choice(["NS", "EW"])
            direction = random.choice([1, -1])
            lane = random.choice([0, 1])
            v_type = random.choices(["car", "bus", "truck", "bike", "ambulance"], [50, 10, 15, 20, 5])[0]
            v_dummy = Vehicle(axis, direction, lane, v_type)
            safe = True
            dummy_rect = pygame.Rect(v_dummy.x, v_dummy.y, v_dummy.w, v_dummy.h).inflate(40, 40)
            for v in self.vehicles:
                if dummy_rect.colliderect(pygame.Rect(v.x, v.y, v.w, v.h)):
                    safe = False; break
            if safe: self.vehicles.append(v_dummy)

    def check_fail_conditions(self):
        waiting_vehicles = [v for v in self.vehicles if v.speed < 0.5 and not v.passed_intersection]
        if len(waiting_vehicles) > 55: return True
        max_wait = max([v.wait_time for v in waiting_vehicles], default=0)
        return max_wait > 30.0

    def draw_fail_screen(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((40, 0, 0, 220)) 
        self.screen.blit(overlay, (0, 0))
        txt_fail = self.f_big.render("GAME OVER – TRAFFIC SYSTEM FAILED", True, (255, 50, 50))
        txt_reason = self.f_sys.render("CRITICAL TRAFFIC OVERLOAD / DEADLOCK DETECTED", True, (255, 200, 200))
        btn_rect = pygame.Rect(WIDTH//2 - 160, HEIGHT//2 + 50, 320, 60)
        pygame.draw.rect(self.screen, C_ACCENT, btn_rect, border_radius=8)
        pygame.draw.rect(self.screen, (20, 25, 30), btn_rect.inflate(-6, -6), border_radius=6)
        txt_restart = self.f_sys.render("[R] RESTART SIMULATION", True, C_ACCENT)
        self.screen.blit(txt_fail, (WIDTH//2 - txt_fail.get_width()//2, HEIGHT//2 - 80))
        self.screen.blit(txt_reason, (WIDTH//2 - txt_reason.get_width()//2, HEIGHT//2 - 10))
        self.screen.blit(txt_restart, (WIDTH//2 - txt_restart.get_width()//2, HEIGHT//2 + 70))

    def draw_ui(self):
        pygame.draw.rect(self.screen, C_UI_BG, (SIM_W, 0, UI_W, HEIGHT))
        pygame.draw.line(self.screen, C_ACCENT, (SIM_W, 0), (SIM_W, HEIGHT), 2)
        x, y = SIM_W + 20, 20
        self.screen.blit(self.f_sys.render("AI DIAGNOSTIC PANEL", True, C_ACCENT), (x, y))
        y += 40
        self.screen.blit(self.f_sys_sm.render(f"SYSTEM STATUS: {self.status}", True, (255,255,255)), (x, y))
        self.screen.blit(self.f_sys_sm.render(f"SIM SPEED: {self.speed_mult}x", True, (255,255,255)), (x, y+20))
        self.screen.blit(self.f_sys_sm.render(f"ACTIVE VEHICLES: {len(self.vehicles)}", True, (255,255,255)), (x, y+40))
        y += 80
        self.screen.blit(self.f_sys.render("ALGORITHMIC PARAMETERS", True, C_ACCENT), (x, y))
        self.screen.blit(self.f_sys_sm.render("AI Logic: Rule-Based Intelligent Agent", True, (150,200,255)), (x, y+30))
        self.screen.blit(self.f_sys_sm.render("Algorithm: Weighted Priority Selection", True, (150,200,255)), (x, y+50))
        y += 110
        self.screen.blit(self.f_sys.render("TRAFFIC DENSITY (REAL-TIME)", True, C_ACCENT), (x, y))
        n_c = len([v for v in self.vehicles if v.axis == "NS" and not v.passed_intersection and v.speed < 0.5])
        e_c = len([v for v in self.vehicles if v.axis == "EW" and not v.passed_intersection and v.speed < 0.5])
        self.screen.blit(self.f_sys_sm.render(f"NORTH-SOUTH QUEUE: {n_c} units", True, (200,200,200)), (x, y+30))
        self.screen.blit(self.f_sys_sm.render(f"EAST-WEST QUEUE  : {e_c} units", True, (200,200,200)), (x, y+50))
        y += 100
        self.screen.blit(self.f_sys.render("AI REASONING OUTPUT", True, C_ACCENT), (x, y))
        pygame.draw.rect(self.screen, (15,20,25), (x, y+30, UI_W-40, 80), border_radius=5)
        reason_color = (255, 80, 80) if "EMERGENCY" in self.ai.reason else C_ACCENT
        words = self.ai.reason.split(' ')
        lines, curr = [], []
        for w in words:
            if len(' '.join(curr + [w])) < 35: curr.append(w)
            else: lines.append(' '.join(curr)); curr = [w]
        lines.append(' '.join(curr))
        for i, l in enumerate(lines): self.screen.blit(self.f_sys_sm.render(l, True, reason_color), (x+10, y+40 + (i*20)))
        y = HEIGHT - 150
        self.screen.blit(self.f_sys.render("CONTROLS", True, C_ACCENT), (x, y))
        self.screen.blit(self.f_sys_sm.render("[P] Play / Pause", True, (150,150,150)), (x, y+30))
        self.screen.blit(self.f_sys_sm.render("[R] Restart Simulation", True, (150,150,150)), (x, y+50))
        self.screen.blit(self.f_sys_sm.render("[Up/Down] Sim Speed", True, (150,150,150)), (x, y+70))

    def run(self):
        dt = 1/60
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: pygame.quit(); return
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_p and self.state == "SIM": self.status = "PAUSED" if self.status == "RUNNING" else "RUNNING"
                    if event.key == pygame.K_r: 
                        self.vehicles.clear(); self.ai = TrafficController()
                        self.state = "SIM"; self.status = "RUNNING"; self.speed_mult = 1.0
                    if event.key == pygame.K_UP: self.speed_mult = min(5.0, self.speed_mult + 0.5)
                    if event.key == pygame.K_DOWN: self.speed_mult = max(0.5, self.speed_mult - 0.5)

            if self.state == "INTRO":
                if self.intro.update_and_draw(): self.state = "SIM"
            else:
                self.env.render()
                self.env.render_signals(self.ai.signals, self.ai.timer)
                if self.state == "SIM" and self.status == "RUNNING":
                    self.spawn_traffic()
                    self.ai.update(self.vehicles, dt * self.speed_mult)
                    self.process_vehicles(dt)
                    if self.check_fail_conditions(): self.state = "GAMEOVER"; self.status = "FAIL"
                for v in self.vehicles: v.draw(self.screen)
                self.vehicles = [v for v in self.vehicles if -200 < v.x < SIM_W+200 and -200 < v.y < SIM_H+200]
                self.draw_ui()
                if self.state == "GAMEOVER": self.draw_fail_screen()

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    SimulationApp().run()