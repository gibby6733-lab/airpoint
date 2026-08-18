export const metadata = {
  title: "About AirPoint",
  description: "Learn about AirPoint and its weather and moisture calculation tools.",
};

export default function About() {
  return (
    <main className="site">
      <section className="hero">
        <div className="container">
          <div className="badge">AIRPOINT</div>
          <h1>About AirPoint</h1>
          <p className="heroText">
            Simple, useful weather and moisture calculations.
          </p>
        </div>
      </section>

      <section className="content">
        <div className="container narrow">
          <h2>What is AirPoint?</h2>
          <p>
            AirPoint is a free collection of weather and moisture calculation
            tools designed to make technical information easier to understand.
          </p>

          <p>
            Our tools help users calculate dew point, understand humidity,
            estimate condensation risk, and explore relationships between
            temperature and moisture.
          </p>

          <h2>Our goal</h2>
          <p>
            We focus on clear calculations, straightforward explanations, and
            tools that are fast and easy to use.
          </p>

          <h2>Our calculations</h2>
          <p>
            AirPoint uses established mathematical formulas and presents the
            results in a simple format. Results are estimates and should be
            evaluated alongside real-world conditions when decisions require
            professional judgment.
          </p>
        </div>
      </section>
    </main>
  );
}