import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class AdManager {

    public static void main(String[] args) {
        List<String> ads = List.of("Coca", "Apple", "Coca", "Nike", "Coca", "Apple", "Nike");
        Map<String, Long> adCounts = countAds(ads);
        System.out.println("Ad Counts: " + adCounts);
        boolean isOverrepresented = checkOverrepresentation(adCounts, ads.size());
        System.out.println("Is any ad overrepresented? " + isOverrepresented);
    }

    public static Map<String, Long> countAds(List<String> ads) {
        Map<String, Long> adCountMap = new HashMap<>();
        for (String ad : ads) {
            adCountMap.put(ad, 1L); 
        }
        return adCountMap;
    }

    public static boolean checkOverrepresentation(Map<String, Long> adCounts, int totalAds) {
        for (Long count : adCounts.values()) {
            // Vérification si une annonce représente plus de 40 % des affichages
            if (count > totalAds * 0.4) {
                return true;
            }
        }
        return false;
    }
}

