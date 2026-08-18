export const metadata = {
  title: "Privacy Policy | AirPoint",
  description:
    "AirPoint privacy policy and information about cookies, advertising, and data use.",
};

export default function Privacy() {
  return (
    <main className="site">
      <section className="hero">
        <div className="container">
          <div className="badge">AIRPOINT</div>
          <h1>Privacy Policy</h1>
          <p className="heroText">
            How AirPoint handles information and advertising technologies.
          </p>
        </div>
      </section>

      <section className="content">
        <div className="container narrow">
          <p>
            <strong>Last updated: August 18, 2026</strong>
          </p>

          <h2>Information we collect</h2>
          <p>
            AirPoint is designed to provide calculation tools without requiring
            an account. Information you enter into a calculator is used to
            perform the requested calculation.
          </p>

          <h2>Cookies and advertising</h2>
          <p>
            If advertising is enabled on AirPoint, third-party vendors,
            including Google, may use cookies to serve ads based on a user's
            visits to AirPoint or other websites.
          </p>

          <p>
            Users may manage personalized advertising preferences through
            Google Ads Settings.
          </p>

          <h2>Third-party services</h2>
          <p>
            AirPoint may use third-party services for hosting, analytics,
            security, search, or advertising. Those services may process
            information according to their own policies.
          </p>

          <h2>Changes</h2>
          <p>
            This policy may be updated as AirPoint changes. The updated date
            above indicates when it was last revised.
          </p>
        </div>
      </section>
    </main>
  );
}