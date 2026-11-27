from scripts.extract_noaa_southern_flounder import (
    is_target_record,
    normalize,
    target_terms,
)


PROFILE = {
    "common_name": "Southern flounder",
    "scientific_name": "Paralichthys lethostigma",
    "aliases": ["flounder"],
}


def test_normalize_collapses_punctuation_and_case():
    assert normalize("  PARALICHTHYS   lethostigma (Jordan & Gilbert) ") == (
        "paralichthys lethostigma jordan gilbert"
    )


def test_matches_exact_scientific_name():
    assert is_target_record({"Species": "Paralichthys lethostigma"}, target_terms(PROFILE))


def test_matches_exact_common_name_field():
    assert is_target_record({"CommonName": "Southern flounder"}, target_terms(PROFILE))


def test_matches_scientific_name_with_authority_suffix():
    assert is_target_record(
        {"SpeciesCommonName": "Paralichthys lethostigma Jordan & Gilbert, 1884"},
        target_terms(PROFILE),
    )


def test_does_not_match_generic_flounder_alias_alone():
    assert not is_target_record({"CommonName": "Flounder"}, target_terms(PROFILE))


def test_does_not_match_other_flounder_species():
    assert not is_target_record(
        {
            "Species": "Paralichthys dentatus",
            "CommonName": "Summer flounder",
            "SpeciesCommonName": "Paralichthys dentatus (Linnaeus, 1766)",
        },
        target_terms(PROFILE),
    )
