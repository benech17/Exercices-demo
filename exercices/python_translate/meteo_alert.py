class Shelter:
    def __init__(self, id, digital, sun_exposure, city):
        self.id = id
        self.digital = digital
        self.sun_exposure = sun_exposure  # Assuming sun_exposure is a string, "N/A" if not applicable
        self.city = city

    def __str__(self):
        return f"Vitrine {self.id} : id = {self.id}, digital = {self.digital}, sunExposure = {self.sun_exposure}, city = \"{self.city}\""


def filter_digital_shelters(shelters):
    result = []

    for shelter in shelters:
        if shelter.digital:
            try:
                sun_exposure_hours = int(shelter.sun_exposure)
                if sun_exposure_hours > 6:
                    result.append(shelter)
                    # Displaying the details of the shelter to be monitored
                    print(shelter)
            except ValueError:
                # This block will handle non-integer sun_exposure values, which should not happen for digital shelters
                print(f"Invalid sun exposure value for digital shelter with id: {shelter.id}")

    return result


if __name__ == "__main__":
    shelters = [
        Shelter(1, True, "7", "Paris"),
        Shelter(2, True, "5", "Lyon"),
        Shelter(3, False, "N/A", "Marseille"),
        Shelter(4, True, "8", "Bordeaux"),
        Shelter(5, True, "9", "Nice"),
        Shelter(6, True, "2", "Lille"),
    ]

    filtered_shelters = filter_digital_shelters(shelters)

    # The result should display details of Shelter 1 and Shelter 4
