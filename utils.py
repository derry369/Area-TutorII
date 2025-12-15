from owlready2 import get_ontology, sync_reasoner
import numpy as np

onto_path = "./"
onto = get_ontology("AreaTutorII.owl").load()
#sync_reasoner()  # optional reasoning

# ------------------- SHAPE FUNCTIONS -------------------
def get_shapes():
    return list(onto.Shape.instances())

def get_lesson(shape):
    for lesson in onto.Lesson.instances():
        if shape in lesson.illustratesShape:
            return lesson
    return None

def get_examples(shape):
    lesson = get_lesson(shape)
    return list(lesson.hasExample) if lesson else []

def get_formula(shape):
    return shape.hasFormula[0].formulaText

# ------------------- AREA CALCULATION -------------------
def compute_area(shape, dims):
    formula = get_formula(shape)
    local_vars = {d: val for d, val in dims.items()}
    local_vars['pi'] = np.pi
    try:
        area = eval(formula.replace('^', '**'), {}, local_vars)
        return float(area)
    except Exception as e:
        print("Error computing area:", e)
        return None

# ------------------- UNIT CHECK -------------------
def check_unit(dims, expected_units):
    for d_name, d_info in dims.items():
        if d_info['unit'] not in expected_units:
            return False
    return True

# ------------------- MISCONCEPTION DETECTION -------------------
def detect_misconceptions(shape, student_value, correct_value, dims, unit_used):
    tol = 1e-3 * correct_value
    mistakes = []

    # 1. Numeric correctness
    if abs(student_value - correct_value) > tol:
        for mis in onto.Misconception.instances():
            if mis.relatesToShape[0] == shape:
                # Use keyword matching in description as simple detection logic
                text = mis.misconceptionText.lower()
                if shape.name.lower() in text:
                    mistakes.append(mis.misconceptionText)

    # 2. Unit check
    if not check_unit({k: {"unit": v['unit']} for k,v in dims.items()}, [unit_used]):
        mistakes.append("Wrong unit used")

    return mistakes

# ------------------- MULTILEVEL HINTS -------------------
def get_hint(shape, level=1):
    hints = {
        "Triangle": [
            "Hint 1: Area = 1/2 × base × height",
            "Hint 2: Ensure you are using perpendicular height, not slanted side",
            "Hint 3: Double-check units and multiply base × height ÷ 2"
        ],
        "Rectangle": [
            "Hint 1: Area = length × width",
            "Hint 2: Do not add sides, multiply them",
            "Hint 3: Check units"
        ],
        "Square": [
            "Hint 1: Area = side × side",
            "Hint 2: Ensure you are not using circle formula π × side²",
            "Hint 3: Units check"
        ],
        "Parallelogram": [
            "Hint 1: Area = base × height",
            "Hint 2: Use perpendicular height, not slanted side",
            "Hint 3: Units check"
        ],
        "Trapezium": [
            "Hint 1: Area = 1/2 × (base1 + base2) × height",
            "Hint 2: Average the two bases, do not just multiply one",
            "Hint 3: Units check"
        ],
        "Circle": [
            "Hint 1: Area = π × radius²",
            "Hint 2: Use radius, not diameter",
            "Hint 3: Include π and correct units"
        ]
    }
    return hints.get(shape.name, ["No hint available"])[level-1]