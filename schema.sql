DROP DATABASE hsociety;
CREATE DATABASE hsociety;
USE hsociety;
CREATE TABLE Users(
  user_id int4 AUTO_INCREMENT,
  u_fname varchar(255),
  u_lname varchar(255),
  education varchar(255),
  year_of_grad int4,
  password varchar(255),
  email varchar(255) UNIQUE NOT NULL,
  CONSTRAINT users_pk PRIMARY KEY (user_id)
);
CREATE TABLE Skills(
  skill_id int4 AUTO_INCREMENT,
  skill_name varchar(255) NOT NULL,
  PRIMARY KEY(skill_id)
);
CREATE TABLE Groups(
  group_id int4 AUTO_INCREMENT,
  group_name varchar(255) NOT NULL,
  PRIMARY KEY(group_id)
);
CREATE TABLE Interests(
  interest_id int4 AUTO_INCREMENT,
  interest_name varchar(255) NOT NULL,
  PRIMARY KEY(interest_id)
);
CREATE TABLE Hackathons(
  hackathon_id int4 AUTO_INCREMENT,
  hackathon_name varchar(255) UNIQUE NOT NULL,
  PRIMARY KEY(hackathon_id)
);

CREATE TABLE H_has_U(
  h_id int4,
  u_id int4,
  FOREIGN KEY(u_id) REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY(h_id) REFERENCES Hackathons(hackathon_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE G_has_U(
  g_id int4,
  u_id int4,
  FOREIGN KEY(u_id) REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY(g_id) REFERENCES Groups(group_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE U_has_S(
  s_id int4,
  u_id int4,
  FOREIGN KEY(u_id) REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY(s_id) REFERENCES Skills(skill_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE U_has_I(
  i_id int4,
  u_id int4,
  FOREIGN KEY(u_id) REFERENCES Users(user_id) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY(i_id) REFERENCES Interests(interest_id) ON DELETE CASCADE ON UPDATE CASCADE
);
