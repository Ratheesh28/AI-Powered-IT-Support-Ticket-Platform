
function StatCard({ title, value, description, icon: Icon }) {
    return (
      <div className="stat-card">
  
        <div className="stat-card-top">
          <span>{title}</span>
          <Icon size={22} />
        </div>
  
        <h2>{value}</h2>
  
        <p>{description}</p>
  
      </div>
    );
  }
  
  export default StatCard;
  