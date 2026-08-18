export const metadata = {
  title: "Terms of Use | AirPoint",
  description: "Terms of use for AirPoint weather and moisture calculation tools.",
};

export default function Terms() {
  return (
    <main className="site">
      <section className="hero">
        <div className="container">
          <div className="badge">AIRPOINT</div>
          <h1>Terms of Use</h1>
          <p className="heroText">Terms governing use of AirPoint.</p>
        </div>
      </section>

      <section className="content">
        <div className="container narrow">
          <p>
            <strong>Last updated: August 18, 2026</strong>
          </p>

          <h2>Use of the site</h2>
          <p>
            AirPoint provides free weather and moisture calculation tools and
            educational information.
          </p>

          <h2>Calculation results</h2>
          <p>
            AirPoint's calculations are provided for informational and
            educational purposes. Results are estimates based on the
            information entered.
          </p>

          <h2>Accuracy</h2>
          <p>
            We work to keep AirPoint's formulas and content accurate, but we do
            not guarantee that every result will always be complete, current,
            or error-free.
          </p>

          <h2>Third-party services</h2>
          <p>
            AirPoint may contain links to third-party websites or use
            third-party services. AirPoint is not responsible for their content
            or availability.
          </p>
        </div>
      </section>
    </main>
  );
}