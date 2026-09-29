from typing import List, Dict

SPECIALIST_MAP = [
    ({'chest', 'breath', 'lung', 'cough', 'pneumonia', 'asthma', 'tb', 'tuberculosis'}, ['Pulmonologist', 'Chest Physician']),
    ({'heart', 'cardiac', 'palpitation', 'cholesterol', 'bp', 'pressure', 'angina'}, ['Cardiologist']),
    ({'skin', 'rash', 'eczema', 'psoriasis', 'acne', 'dermatitis', 'allergy'}, ['Dermatologist']),
    ({'brain', 'headache', 'migraine', 'seizure', 'neuro', 'memory', 'stroke', 'dizziness'}, ['Neurologist']),
    ({'bone', 'joint', 'arthritis', 'fracture', 'spine', 'orthopedic', 'back pain'}, ['Orthopedist']),
    ({'stomach', 'gastric', 'liver', 'intestine', 'bowel', 'digestive', 'acid', 'nausea', 'vomiting'}, ['Gastroenterologist']),
    ({'kidney', 'urine', 'renal', 'creatinine', 'dialysis', 'nephro'}, ['Nephrologist']),
    ({'diabetes', 'thyroid', 'hormone', 'insulin', 'glucose', 'metabolic', 'endocrine'}, ['Endocrinologist']),
    ({'eye', 'vision', 'retina', 'cataract', 'glaucoma', 'optic'}, ['Ophthalmologist']),
    ({'ear', 'hearing', 'ent', 'nose', 'throat', 'sinus', 'tonsil'}, ['ENT Specialist']),
    ({'mental', 'anxiety', 'depression', 'stress', 'psychiatric', 'mood', 'bipolar'}, ['Psychiatrist', 'Psychologist']),
    ({'cancer', 'tumor', 'oncology', 'chemotherapy', 'lymphoma', 'biopsy'}, ['Oncologist']),
    ({'child', 'infant', 'pediatric', 'baby', 'adolescent'}, ['Pediatrician']),
    ({'pregnancy', 'gynecology', 'menstrual', 'uterus', 'ovary', 'obstetric'}, ['Gynecologist / Obstetrician']),
]

SPECIALIST_INFO = {
    'Pulmonologist': 'Specializes in lung and respiratory system disorders.',
    'Cardiologist': 'Specializes in heart and cardiovascular diseases.',
    'Dermatologist': 'Specializes in skin, hair, and nail conditions.',
    'Neurologist': 'Specializes in brain, spinal cord, and nervous system.',
    'Orthopedist': 'Specializes in bones, joints, muscles, and spine.',
    'Gastroenterologist': 'Specializes in digestive system and liver.',
    'Nephrologist': 'Specializes in kidney function and diseases.',
    'Endocrinologist': 'Specializes in hormones and metabolic disorders.',
    'Ophthalmologist': 'Specializes in eye diseases and vision.',
    'ENT Specialist': 'Specializes in ear, nose, and throat disorders.',
    'Psychiatrist': 'Specializes in mental health and psychiatric disorders.',
    'Psychologist': 'Provides therapy and counseling for mental health.',
    'Oncologist': 'Specializes in cancer diagnosis and treatment.',
    'Pediatrician': 'Specializes in healthcare for children and adolescents.',
    'Gynecologist / Obstetrician': "Specializes in women's reproductive health.",
    'Chest Physician': 'Specializes in chest and respiratory diseases.',
    'General Physician': 'Provides primary care for general health concerns.',
}


def suggest_specialist(symptoms: List[str]) -> List[Dict]:
    """Return ranked specialist suggestions based on symptoms."""
    text = ' '.join(symptoms).lower()
    found: Dict[str, int] = {}
    for keywords, specialists in SPECIALIST_MAP:
        for kw in keywords:
            if kw in text:
                for sp in specialists:
                    found[sp] = found.get(sp, 0) + 1
                break

    if not found:
        return [{
            'specialist': 'General Physician',
            'description': SPECIALIST_INFO.get('General Physician', ''),
            'priority': 1
        }]

    ranked = sorted(found.items(), key=lambda x: x[1], reverse=True)
    return [
        {
            'specialist': sp,
            'description': SPECIALIST_INFO.get(sp, 'Specialist in related medical field.'),
            'priority': i + 1
        }
        for i, (sp, _) in enumerate(ranked[:4])
    ]
