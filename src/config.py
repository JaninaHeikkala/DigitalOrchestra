# Camera Settings
WEBCAM_WIDTH = 320
WEBCAM_HEIGHT = 240

# OpenCV Settings
MIN_AREA = 100      # If contours are bigger than this area, sounds are played
BLUR_SIZE = 10

# Motion Settings
noteSleep = 0.05
loopPlayOn = False # True = Play looped saved melodies, False = Off

# Drum Settings
drumPlayOn = False    # True = Turn on Drum Motion Play, False = Off

# Drum Tread(s)
drumKickOn = False      # Thread for Kick Drum

ambientOn = True # Ambient background chord

thresHoldSensitivity = 80

# List of Available sythesizers
synthList = [
    (0,'dull_bell'),
    (1,'pretty_bell'),
    (2, 'sine'),
    (3, 'square'),
    (4,'pulse'),
    (5,'subpulse'),
    (6,'dtri'),
    (7,'dpulse'),
    (8,'fm'),
    (9,'mod_fm'),
    (10,'mod_saw'),
    (11,'mod_dsaw'),
    (12,'mod_sine'),
    (13,'mod_tri'),
    (14,'mod_pulse'),
    (15,'supersaw'),
    (16,'hoover'),
    # (17,'synth_violin'), does not exist anymore ?
    (18,'pluck'),
    (19,'piano'),
    (20,'growl'),
    (21,'dark_ambience'),
    # (22,'dark_sea_horn'), does not exist anymore ?
    (23,'hollow'),
    (24,'zawa'),
    (25,'noise'),
    (26,'gnoise'),
    (27,'bnoise'),
    (28,'cnoise'),
    (29,'dsaw'),
    (30,'tb303'),
    (31,'blade'),
    (32,'prophet'),
    (33,'saw'),
    (34,'beep'),
    (35,'tri'),
    (36,'chiplead'),
    (37,'chipbass'),
    (38,'chipnoise'),
    (39,'tech_saws'),
    (40,'sound_in'),
    (41,'sound_in_stereo')
]
# Select synthPicks numbers above comma separated (any number or order)
redSynthPicks = [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 37, ]
greenSynthPicks = [2, 19, ]
blueSynthPicks = [ 21, 23, ]

# Lists of notes in each octave range
octaveList = [
(0,[ 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 ]),
(1,[ 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23 ]),
(2,[ 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35 ]),
(3,[ 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47 ]),
(4,[ 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59 ]),
(5,[ 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71 ]),
(6,[ 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83 ]),
(7,[ 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95 ]),
(8,[ 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107 ]),
(9,[ 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119 ]),
(10,[ 120, 121, 122, 123, 124, 125, 126, 127 ])
]
# Select octavePicks numbers above comma separated (any number an order)
octavePicks = [ 4, 5, 6 ]

# Define scale intervals for various scales
scalesIntervals = {
    "major": [0, 2, 4, 5, 7, 9, 11],  # C Major scale
    "minor": [0, 2, 3, 5, 7, 8, 10],  # C Minor scale
    "pentatonic": [0, 2, 4, 7, 9],    # C Pentatonic scale
}

# List of Available Drum Sounds
# Add Reference number Selections to drumPicks list below
drumList = [
(0,'drum_heavy_kick'),
(1,'drum_tom_mid_soft'),
(2,'drum_tom_mid_hard'),
(3,'drum_tom_lo_soft'),
(4,'drum_tom_lo_hard'),
(5,'drum_tom_hi_soft'),
(6,'drum_tom_hi_hard'),
(7,'drum_splash_soft'),
(8,'drum_splash_hard'),
(9,'drum_snare_soft'),
(10,'drum_snare_hard'),
(11,'drum_cymbal_soft'),
(12,'drum_cymbal_hard'),
(13,'drum_cymbal_open'),
(14,'drum_cymbal_closed'),
(15,'drum_cymbal_pedal'),
(16,'drum_bass_soft'),
(17,'drum_bass_hard'),
(18,'drum_cowbell'),
(19,'drum_roll')
]
# Select drumPicks numbers above comma separated (any number an order)
redDrumPicks = [0, 2, 4, 10, 14, 14, 14, 15, 16]
greenDrumPicks = [3, 5, 11, 14]
blueDrumPicks = [3, 7, 11]

sampleList = [
    (0, 'bass_hit_c'),
    (1, 'bass_hard_c'),
    (2, 'bass_thick_c'),
    (3, 'bass_drop_c'),
    (4, 'bass_woodsy_c'),
    (5, 'bass_voxy_c'),
    (6, 'bass_voxy_hit_c'),
    (7, 'bass_dnb_f'),
]