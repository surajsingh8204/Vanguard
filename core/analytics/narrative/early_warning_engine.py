class EarlyWarningEngine:

    def generate(

        self,

        forecasts
    ):

        warnings = []

        for item in forecasts:

            warning_score = (

                0.4 * item["score"]

                +

                0.3 * item["influence"]

                +

                0.3 * item["emergence"]

            )

            reasons = []

            if item["influence"] > 0.30:

                reasons.append(
                    "High influence"
                )

            if item["emergence"] > 1.0:

                reasons.append(
                    "Emerging narrative"
                )

            if item["slope"] > 2:

                reasons.append(
                    "Strong growth trend"
                )

            warnings.append({

                "narrative":
                item["narrative"],

                "warning_score":
                round(
                    float(warning_score),
                    2
                ),

                "reasons":
                reasons,

                "volume":
                item["current_volume"]
            })

        warnings.sort(

            key=lambda x:
            x["warning_score"],

            reverse=True

        )

        return warnings
    
    def display(
        self,
        warnings
    ):

        print("\n" + "=" * 60)
        print("⚠ EARLY WARNING REPORT")
        print("=" * 60)

        for item in warnings[:10]:

            print(
                f"\n🚨 {item['narrative']}"
            )

            print(
                f"Warning Score: "
                f"{item['warning_score']}"
            )

            print(
                f"Volume: "
                f"{item['volume']}"
            )

            if item["reasons"]:

                print("\nReasons:")

                for reason in item["reasons"]:

                    print(
                        f"✓ {reason}"
                    )

            print("-" * 40)