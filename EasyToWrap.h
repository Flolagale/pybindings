#include <string>

/* This c++ header file is part of the pybindings project
as a relevant c++ sample for testing purpose. It is no meant
to do anything useful unless you really want a class that
contains an integer and a string. */
class EasyToWrap
{
public:
    EasyToWrap()
        : m_integer(2), m_message("Hello Kitty!") {}
    EasyToWrap(const EasyToWrap& original)
        : m_integer(original.m_integer), m_message(original.m_message) {}
    ~EasyToWrap() {}

    void setInteger(int integer) {this->m_integer = integer;}

    const std::string& getMessage() const {return this->m_message;}

    int setContent(int integer, const std::string* message)
    {
        this->m_integer = integer;
        this->m_message = *message;
        return this->m_integer;
    }

    void fillStringWithMessage(std::string** message)
    {
        delete *message;
        *message = new std::string(this->m_message);
    }

private:
    int             m_integer;
    std::string     m_message;
};
