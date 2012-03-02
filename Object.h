#include <string>

class Object
{
public:
	Object()
		: m_integer(2), m_message("Hello Kitty!") {}
	Object(const Object& original)
		: m_integer(original.m_integer), m_message(original.m_message) {}
	~Object() {}

	void setInteger(int integer) {this->m_integer = integer;}

	const std::string& getMessage() const {return this->m_message;}

private:
	int				m_integer;
	std::string		m_message;
};
