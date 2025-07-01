m_n = 1.67492749804e-27         # kg (mass of neutron)
neutron_mass = 1.67492749804e-27
hbar = 1.0545718176461565e-34   # J.s (reduced Planck's constant)
e = 1.602176634e-19             # C (charge of electron)
elementary_charge = 1.602176634e-19
h = 6.62607015e-34              # J.s (Planck's constant)
k = 1.380649e-23                # J/K (Boltzmann's constant)
Boltzmann = 1.380649e-23        # J/K (Boltzmann's constant)

full_dict = {
    'Boltzmann constant in eV/K': 8.617333262e-5,
}

def value(name):
    if name in full_dict.keys():
        return full_dict[name]
    else:
        return globals()[name]
