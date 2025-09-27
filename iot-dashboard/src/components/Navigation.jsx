import { Link, useLocation } from 'react-router-dom';

const Navigation = () => {
  const location = useLocation();

  const navItems = [
    {
      path: '/',
      name: 'Dashboard',
      icon: '📊',
      description: 'Données CSV en temps réel'
    },
    {
      path: '/analysis',
      name: 'Analyse',
      icon: '📈',
      description: 'Analyse et statistiques'
    }
  ];

  return (
    <nav style={{
      backgroundColor: 'white',
      boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
      borderBottom: '1px solid #e5e7eb'
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
        padding: '0 24px'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          height: '64px'
        }}>
          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <div style={{
              fontSize: '24px'
            }}>🗄️</div>
            <div>
              <h1 style={{
                fontSize: '20px',
                fontWeight: 'bold',
                color: '#111827',
                margin: 0
              }}>
                IoT Telemetry
              </h1>
              <p style={{
                fontSize: '12px',
                color: '#6b7280',
                margin: 0
              }}>
                Analyse des données CSV
              </p>
            </div>
          </div>

          {/* Navigation */}
          <div style={{ display: 'flex', gap: '4px' }}>
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;

              return (
                <Link
                  key={item.path}
                  to={item.path}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '8px 16px',
                    borderRadius: '8px',
                    textDecoration: 'none',
                    transition: 'all 0.2s',
                    backgroundColor: isActive ? '#dbeafe' : 'transparent',
                    color: isActive ? '#1d4ed8' : '#6b7280',
                    border: isActive ? '1px solid #93c5fd' : '1px solid transparent'
                  }}
                  onMouseOver={(e) => {
                    if (!isActive) {
                      e.target.style.backgroundColor = '#f9fafb';
                      e.target.style.color = '#111827';
                    }
                  }}
                  onMouseOut={(e) => {
                    if (!isActive) {
                      e.target.style.backgroundColor = 'transparent';
                      e.target.style.color = '#6b7280';
                    }
                  }}
                >
                  <span style={{ fontSize: '16px' }}>{item.icon}</span>
                  <div style={{ textAlign: 'left' }}>
                    <div style={{
                      fontSize: '14px',
                      fontWeight: '500'
                    }}>
                      {item.name}
                    </div>
                    <div style={{
                      fontSize: '12px',
                      color: '#6b7280'
                    }}>
                      {item.description}
                    </div>
                  </div>
                </Link>
              );
            })}
          </div>

          {/* Status */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <div style={{
              width: '8px',
              height: '8px',
              backgroundColor: '#10b981',
              borderRadius: '50%'
            }}></div>
            <span style={{
              fontSize: '14px',
              color: '#6b7280'
            }}>
              CSV Actif
            </span>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navigation;