from collections import defaultdict
from divisiones import unique_divisions

def remove_redundant_divisions(unique_divisions):
    # Dictionary to store the cleaned data
    cleaned_dict = {}

    for estado, municipios in unique_divisions.items():
        # Use a dictionary to track unique divisions in this state
        division_map = defaultdict(list)
        
        for municipio, divisiones in municipios.items():
            for division in divisiones:
                # Store municipio under its division in division_map
                division_map[division].append(municipio)
        
        # Rebuild the cleaned data structure for this state
        cleaned_dict[estado] = {}
        for division, municipios_list in division_map.items():
            # Use the first municipio associated with each division as representative
            cleaned_dict[estado][municipios_list[0]] = [division]

    return cleaned_dict

# Apply the function
cleaned_unique_divisions = remove_redundant_divisions(unique_divisions)

# Output the result
print(cleaned_unique_divisions)