
Technical Documentation: difference.py & image_processor.py
Project: Neon Detective — Spot the Difference
Language: Python 3
Dependencies: OpenCV (cv2), random, tkinter.messagebox

1. Module Overview
These two modules form the entire image-processing layer of the game. They are fully decoupled from the GUI and game engine — no tkinter widgets, no game state — which means the logic can be tested independently and the rest of the project can treat them as a black box.
Responsibilities:

difference.py — Data model. Represents a single hidden alteration: its bounding box, type, and found state. Provides hit-testing and geometry helpers.
image_processor.py — Processing engine. Loads an image, generates five non-overlapping altered regions on a copy, applies a randomised visual alteration to each, and stores the resulting Difference objects.

The game engine communicates with these modules only through three public attributes: processor.original, processor.modified, and processor.differences.

2. difference.py — Class: Difference
2.1 Purpose
A lightweight data-transfer object. Each instance represents one hidden alteration placed in the modified image. The game engine stores these in a list and queries them on every click event.
2.2 Constructor
pythondef __init__(self, x, y, w, h, diff_type):
    self.x         = x           # left edge, in original image pixels
    self.y         = y           # top edge, in original image pixels
    self.w         = w           # width of the altered bounding box
    self.h         = h           # height of the altered bounding box
    self.diff_type = diff_type   # string identifier for the alteration type
    self.found     = False       # toggled True when the player clicks correctly
All coordinates are stored in original image pixel-space, not display pixel-space. The game engine converts between the two at render time using its stored scale_x / scale_y factors.
2.3 Methods
contains_click(x, y, tolerance=25) → bool
Returns True if the point (x, y) falls within the bounding box expanded by tolerance pixels on all four sides.
pythondef contains_click(self, x, y, tolerance=25):
    return (
        self.x - tolerance <= x <= self.x + self.w + tolerance and
        self.y - tolerance <= y <= self.y + self.h + tolerance
    )
The default tolerance of 25 px gives fair, forgiving detection while still requiring the click to be near the difference. This tolerance is applied in image-pixel space after the inverse scaling transform has been applied by the game engine, keeping accuracy consistent regardless of window size.

get_center() → tuple(int, int)
Returns the pixel coordinates of the bounding box centre.
pythondef get_center(self):
    return self.x + self.w // 2, self.y + self.h // 2
Used by the game engine to position the feedback circle on both canvases.

get_radius() → int
Returns half the length of the longer edge of the bounding box.
pythondef get_radius(self):
    return max(self.w, self.h) // 2
Used as the base radius when drawing highlight circles, ensuring the circle fully encloses the altered region regardless of its aspect ratio.
2.4 Design Notes

Coordinate system: Coordinates are stored in full-resolution image pixels. The game engine translates them to canvas display coordinates at render time. This decouples the model from the view — the display size can change without touching this class.
found flag: Once set to True, the game engine skips this object in the click loop. The flag prevents double-counting and controls whether a blue (reveal) or red (found) circle is drawn.
Immutability of geometry: x, y, w, h are set once at construction and never modified. Only found changes during gameplay.


3. image_processor.py — Class: ImageProcessor
3.1 Purpose
Procedural image-manipulation engine. Loads any image format that OpenCV supports (JPEG, PNG, BMP, TIFF, WebP), produces an independent modified copy, and plants five hidden differences across it. Maintains three public attributes queried by the game engine.
3.2 load_image(path) → bool
pythondef load_image(self, path):
    image = cv2.imread(path)           # supports JPEG, PNG, BMP, TIFF, WebP
    if image is None:
        messagebox.showerror(...)      # shows dialog, returns False
        return False
    self.original    = image           # stored unmodified
    self.modified    = image.copy()    # independent array for all edits
    self.differences = []              # clears state from any previous round
    self.create_differences()
    if len(self.differences) < 5:
        messagebox.showwarning(...)    # image too small
    return True
Calling load_image() on a new image fully resets all three public attributes before generating new differences. This guarantees that loading a new image mid-game always produces a clean slate for the game engine.
The two arrays (original and modified) are independent after image.copy(). All pixel edits go to modified only, so the original is always preserved for side-by-side display.

3.3 check_overlap(new_box, boxes) → bool
pythondef check_overlap(self, new_box, boxes):
    x, y, w, h = new_box
    padding = 35
    for bx, by, bw, bh in boxes:
        if not (
            x + w + padding < bx or
            x > bx + bw + padding or
            y + h + padding < by or
            y > by + bh + padding
        ):
            return True   # overlap detected
    return False
Uses axis-aligned bounding-box separation testing with a 35 px gap buffer. A new box is only accepted if it is separated from every existing box by at least 35 pixels on all axes, preventing visual crowding and ensuring no two alterations are close enough to be confused for one another.

3.4 create_differences() — Placement Algorithm
Iterates up to 1,500 times attempting to place five non-overlapping alterations:

Box dimensions are sampled uniformly from 55–95 px, producing natural size variation.
For images smaller than the minimum box size, dimensions are clamped to image_dimension / 6, allowing the game to function on any reasonably sized photograph.
Each position is constrained to keep the box at least 20 px from every image edge, preventing clipping by panel borders.
The alteration type is selected with uniform probability from all seven types, so every load produces a different combination.
The 1,500-attempt cap guarantees termination. On typical photographs this limit is never reached; it only matters for pathologically small images.

Five Difference objects are appended to self.differences only after successful placement, so the list is always an accurate count of visible, non-overlapping alterations.

3.5 apply_difference(x, y, w, h, diff_type) — Alteration Types
All seven types operate on self.modified only. Where pixel arithmetic is needed, cv2.add() and cv2.subtract() are used instead of direct NumPy operations — these functions clamp results to [0, 255], preventing channel wrap-around artefacts.
TypeOpenCV TechniqueVisual EffectDifficultycolour_shiftcv2.add / cv2.subtract on B and G channelsBlue channel +45, green channel −25 — cold, slightly desaturated patchMedium — subtle on complex texturesblurcv2.GaussianBlur with 21×21 kernelSoft, out-of-focus rectangleLow–Medium — obvious near edgesbrightnessconvertScaleAbs alpha=1.15, beta=45Region brightened by scaling then offsetLow — distinct on dark backgroundsdark_patchconvertScaleAbs alpha=0.55, beta=0Region darkened to 55% of original luminanceLow–Medium — very visible on bright imagesedge_linecv2.line horizontal across centreNear-black 4 px horizontal lineHigh — easy to overlook in busy imagestiny_symbolcv2.circle + cv2.line cross-hairDark circle with horizontal bar — resembles a scope reticleHigh — blends into high-frequency texturetexture_noisecv2.add / cv2.subtract on R and B channelsRed channel boosted, blue reduced — warm colour castMedium–High — barely noticeable on warm images

4. Interaction Between Modules
StepActionOutcome1Game engine calls processor.load_image(path)Image loaded; original, modified, differences initialised2Game engine reads processor.original / .modifiedArrays converted to RGB via cv2.cvtColor, wrapped in ImageTk for canvas display3Player clicks modified canvasEngine maps canvas coords to image-pixel space, calls diff.contains_click(real_x, real_y) on each unfound Difference4Match found → diff.found = TrueObject skipped in future clicks; red circle drawn using get_center() and get_radius()5Reveal button pressedEngine iterates all processor.differences regardless of found state, draws blue circles using the same geometry helpers

5. Design Decisions & Justifications
Separation of concerns. Neither module imports tkinter or references game state (score, mistakes, timer). The image pipeline can be unit-tested independently or swapped without touching the GUI.
In-place modification with a copy. image.copy() creates two independent NumPy arrays. Edits to modified never affect original, which is critical because the GUI renders both simultaneously and the player must compare them directly.
Retry-based placement. A retry loop is simpler and more flexible than grid-based placement. It produces irregular distributions that feel human-planted rather than algorithmically spaced, improving gameplay feel. The 1,500-attempt cap guarantees termination.
Saturating arithmetic. cv2.add() and cv2.subtract() clamp to [0, 255]. Direct NumPy addition wraps around (255 + 1 = 0), which would produce visible artefacts. The OpenCV functions prevent this without requiring explicit np.clip() calls.
Pixel-space coordinates. Storing difference coordinates in full-resolution pixel space, not display-canvas space, decouples the model from the view. The display dimensions can change without affecting Difference objects.

6. Error Handling
ScenarioHandlingUser FeedbackFile path invalid or unreadablecv2.imread() returns None; load_image() returns False immediatelymessagebox.showerror: "Image could not be loaded."Image too small for 5 non-overlapping boxesRetry loop exits; fewer than 5 Difference objects appendedmessagebox.showwarning: "Could not create all 5 clues. Please use a bigger image."ROI slice out of rangePlacement algorithm enforces x + w ≤ width − 20 and y + h ≤ height − 20 before calling apply_difference()No error raised — bounds checked at placement stageChannel value overflow / underflowcv2.add / cv2.subtract clamps to [0, 255]No visible artefacts — transparent to the user

7. Key Configurable Values
ParameterValueEffecttolerance in contains_click()25 pxHit-test expansion in image-pixel spacepadding in check_overlap()35 pxMinimum gap enforced between all bounding boxesBox size range55–95 pxWidth and height of each alteration regionEdge margin20 pxMinimum distance from image borderMax placement attempts1,500Retry cap guaranteeing loop terminationTarget difference count5Number of hidden alterations generated per image load
