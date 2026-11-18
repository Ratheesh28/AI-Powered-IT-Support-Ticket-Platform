function StatCard({ title, value, description, icon: Icon, tone = "indigo" }) {
  return (
    <article className={`stat-card tone-${tone}`}>
      <div className="stat-card-top">
        <span>{title}</span>
        {Icon ? (
          <span className="stat-icon" aria-hidden="true">
            <Icon size={18} />
          </span>
        ) : null}
      </div>

      <h2>{value}</h2>
      <p>{description}</p>
    </article>
  );
}

export default StatCard;
