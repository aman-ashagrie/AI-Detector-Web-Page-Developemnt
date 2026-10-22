import photo1 from '../assets/lloyd-headshot.png.jpg';


export default function About() {
  return (
    <div className="page-container">
        <div className="content-box">
        <h2>Meet The Team</h2>
        </div>
      <div className="image-grid">
        
        <div className="image-card">
          <div className="image-1"></div>
          <div className="mini-text-box">
            <h3>Amanuial Ashagrie</h3>
            <p>Hi, my name is Aman, and I am a Bachelor of Computer Science student, Majoring in AI. This is my first AI unit, and only recently found out that this is a third-year course, but I decided to take on the challenge and give myself the environment to rapidly grow. Even though my experience leans more on Software development and less experience in AI. Through this course, I intend to kickstart my AI skillset and develop hands on experience in AI models and working with a team to create a working agentic model. In my spare time, I like to play tennis and play my drum set. I also enjoy social gatherings and connecting with people with different backgrounds.</p>
          </div>
        </div>

        <div className="image-card">
          <div className="image-1"></div>
          <div className="mini-text-box">
            <h3>Nathan Alexander Vuong</h3>
            <p>I’m a 2nd year Data Science student co-majoring in Psychology. Through this unit I hope to further improve my team and communication skills. I believe the end-product that we are designing and creating will provide good experience as well as an opportunity to demonstrate a variety of skills. In my free time I like to practice guitar and read books.</p>
          </div>
        </div>
        <div className="image-card">
          <img src={photo1} alt="Lloyd Cook-Rowe" className="image-1" />
          <div className="mini-text-box">
            <h3>Lloyd Cook-Rowe</h3>
            <p>My name is Lloyd and I will be leading the data preprocessing, scoring logic, model integration and UI construction of the AI text detection webpage project. I am completing this project with my group as a part of my Bachelor of Computer Science to further my understanding of AI, python and web-based application production. When I have time outside of my full-time job and university schedule, I enjoy gaming, connecting with friends and playing tennis as well as basketball. I strive for good results and hope that our team can come together and collaborate to create an outstanding application that is practical, attractive and secure.</p>
          </div>
        </div>

      </div>
      <div className="content-box">
        <h2>About Us</h2>
        <p>We are dedicated to providing accurate AI detection tools. This is the big sample text box in the middle of the About page.</p>
      </div>

    </div>
  );
}