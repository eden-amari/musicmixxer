from typing import List, Dict


class OrganizationService:
    """
    Service responsible for organizing tracks based on different strategies.

    Supported strategies:
    - bpm: sort by tempo
    - energy: sort by energy level
    - valence: sort by mood
    - smart_mix: smooth transitions using multi-feature distance
    """

    DEFAULT_BPM = 120
    DEFAULT_ENERGY = 0.5
    DEFAULT_VALENCE = 0.5

    # Weight configuration (easy to tune later)
    BPM_WEIGHT = 0.3
    ENERGY_WEIGHT = 0.5
    VALENCE_WEIGHT = 0.2

    BPM_NORMALIZATION_FACTOR = 100  # important fix

    @staticmethod
    def organize(tracks: List[Dict], strategy: str = "smart_mix") -> List[Dict]:
        if not tracks:
            return []

        if strategy == "bpm":
            return OrganizationService._by_bpm(tracks)

        if strategy == "energy":
            return OrganizationService._by_energy(tracks)

        if strategy == "valence":
            return OrganizationService._by_valence(tracks)

        if strategy == "smart_mix":
            return OrganizationService._smart_mix(tracks)

        raise ValueError(f"Invalid strategy: {strategy}")

    # -------------------------
    # SIMPLE STRATEGIES
    # -------------------------

    @staticmethod
    def _by_bpm(tracks: List[Dict]) -> List[Dict]:
        return sorted(tracks, key=lambda t: t.get("bpm", OrganizationService.DEFAULT_BPM))

    @staticmethod
    def _by_energy(tracks: List[Dict]) -> List[Dict]:
        return sorted(tracks, key=lambda t: t.get("energy", OrganizationService.DEFAULT_ENERGY))

    @staticmethod
    def _by_valence(tracks: List[Dict]) -> List[Dict]:
        return sorted(tracks, key=lambda t: t.get("valence", OrganizationService.DEFAULT_VALENCE))

    # -------------------------
    # SMART MIX (CORE LOGIC)
    # -------------------------

    @staticmethod
    def _smart_mix(tracks: List[Dict]) -> List[Dict]:
        if len(tracks) <= 2:
            return tracks

        remaining = tracks.copy()

        current = min(
            remaining,
            key=lambda t: t.get("energy", OrganizationService.DEFAULT_ENERGY)
        )

        ordered = [current]
        remaining.remove(current)

        while remaining:
            next_track = min(
                remaining,
                key=lambda t: OrganizationService._distance(current, t)
            )

            ordered.append(next_track)
            remaining.remove(next_track)
            current = next_track

        return ordered

    # -------------------------
    # DISTANCE FUNCTION (FIXED)
    # -------------------------

    @staticmethod
    def _distance(t1: Dict, t2: Dict) -> float:
        """
        Compute similarity distance between two tracks.

        Fixes:
        - Normalized BPM
        - Balanced feature contribution
        """

        bpm1 = t1.get("bpm", OrganizationService.DEFAULT_BPM)
        bpm2 = t2.get("bpm", OrganizationService.DEFAULT_BPM)

        e1 = t1.get("energy", OrganizationService.DEFAULT_ENERGY)
        e2 = t2.get("energy", OrganizationService.DEFAULT_ENERGY)

        v1 = t1.get("valence", OrganizationService.DEFAULT_VALENCE)
        v2 = t2.get("valence", OrganizationService.DEFAULT_VALENCE)

        # 🔥 Normalize BPM difference
        bpm_diff = abs(bpm1 - bpm2) / OrganizationService.BPM_NORMALIZATION_FACTOR

        return (
            OrganizationService.BPM_WEIGHT * bpm_diff +
            OrganizationService.ENERGY_WEIGHT * abs(e1 - e2) +
            OrganizationService.VALENCE_WEIGHT * abs(v1 - v2)
        )