export const metadata = {
  title: "Contact AirPoint",
  description:
    "Contact AirPoint about questions, feedback, or issues with the site.",
};

export default function Contact() {
  return (
    <main className="site">
      <section className="hero">
        <div className="container">
          <div className="badge">AIRPOINT</div>
          <h1>Contact AirPoint</h1>
          <p className="heroText">
            Questions, feedback, or a problem with one of our tools?
          </p>
        </div>
      </section>

      <section className="content">
        <div className="container narrow">
          <h2>We'd like to hear from you</h2>

          <p>
            If you find an issue with a calculation, discover a broken page, or
            have an idea for a useful weather or moisture calculator, we'd like
            to hear from you.
          </p>

          <p>
            <a
              href="https://github.com/gibby6733-lab/airpoint/issues"
              target="_blank"
              rel="noreferrer"
            >
              AirPoint GitHub Issues →
            </a>
          </p>
        </div>
      </section>
    </main>
  );
}